import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import Anthropic from 'https://esm.sh/@anthropic-ai/sdk@0.17.0'
import { corsHeaders, getUser, createAuthClient } from '../_shared/utils.ts'

interface ChatRequest {
  conversationId: string
  message: string
}

serve(async (req) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // Authenticate user
    const user = await getUser(req)
    if (!user) {
      return new Response(
        JSON.stringify({ error: 'Unauthorized' }),
        { status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Parse request
    const { conversationId, message }: ChatRequest = await req.json()

    if (!conversationId || !message) {
      return new Response(
        JSON.stringify({ error: 'Missing conversationId or message' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Create Supabase client with user auth
    const authHeader = req.headers.get('Authorization')!
    const supabase = createAuthClient(authHeader)

    // Get conversation and verify ownership
    const { data: conversation, error: convError } = await supabase
      .from('conversations')
      .select('*, agents(*)')
      .eq('id', conversationId)
      .single()

    if (convError || !conversation) {
      return new Response(
        JSON.stringify({ error: 'Conversation not found' }),
        { status: 404, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    if (conversation.user_id !== user.id) {
      return new Response(
        JSON.stringify({ error: 'Forbidden' }),
        { status: 403, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Get recent messages for context
    const { data: messages } = await supabase
      .from('messages')
      .select('role, content')
      .eq('conversation_id', conversationId)
      .order('created_at', { ascending: true })
      .limit(20)

    // Save user message
    await supabase.from('messages').insert({
      conversation_id: conversationId,
      role: 'user',
      content: message,
    })

    // Build system prompt
    const agent = conversation.agents
    const systemPrompt = `You are ${agent.name}, an AI agent with the role of ${agent.role}.

${agent.description || ''}

Your responsibilities:
- Proactively monitor and analyze data sources assigned to you
- Identify anomalies, trends, and important insights
- Provide clear explanations and actionable recommendations
- Help users understand complex information
- Execute tasks delegated by users

Communication style:
- Be concise and direct
- Focus on actionable insights
- Use data to support your analysis
- Ask clarifying questions when needed`

    // Build messages array
    const conversationMessages = messages || []
    const claudeMessages = [
      ...conversationMessages.map(m => ({
        role: m.role as 'user' | 'assistant',
        content: m.content
      })),
      {
        role: 'user' as const,
        content: message
      }
    ]

    // Call Claude API with streaming
    const anthropic = new Anthropic({
      apiKey: Deno.env.get('CLAUDE_API_KEY')!
    })

    const stream = await anthropic.messages.stream({
      model: 'claude-3-5-sonnet-20241022',
      max_tokens: 4096,
      system: systemPrompt,
      messages: claudeMessages,
    })

    // Create readable stream for SSE
    let fullResponse = ''
    const encoder = new TextEncoder()

    const readableStream = new ReadableStream({
      async start(controller) {
        try {
          for await (const chunk of stream) {
            if (chunk.type === 'content_block_delta' &&
                chunk.delta.type === 'text_delta') {
              const text = chunk.delta.text
              fullResponse += text
              controller.enqueue(encoder.encode(`data: ${JSON.stringify({ text })}\n\n`))
            }
          }

          // Save assistant message
          await supabase.from('messages').insert({
            conversation_id: conversationId,
            role: 'assistant',
            content: fullResponse,
          })

          // Update conversation last_message_at
          await supabase
            .from('conversations')
            .update({ last_message_at: new Date().toISOString() })
            .eq('id', conversationId)

          // Send completion
          controller.enqueue(encoder.encode('data: [DONE]\n\n'))
          controller.close()
        } catch (error) {
          controller.enqueue(encoder.encode(`data: ${JSON.stringify({ error: error.message })}\n\n`))
          controller.close()
        }
      }
    })

    return new Response(readableStream, {
      headers: {
        ...corsHeaders,
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      }
    })

  } catch (error) {
    console.error('Error:', error)
    return new Response(
      JSON.stringify({ error: error.message }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }
})
