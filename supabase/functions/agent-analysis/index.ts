import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import Anthropic from 'https://esm.sh/@anthropic-ai/sdk@0.17.0'
import { corsHeaders, createServiceClient } from '../_shared/utils.ts'

/**
 * This function is triggered by Supabase Cron
 * Schedule: Every hour
 *
 * To set up the cron job, run in Supabase SQL editor:
 *
 * SELECT cron.schedule(
 *   'agent-analysis-hourly',
 *   '0 * * * *', -- Every hour
 *   $$
 *   SELECT
 *     net.http_post(
 *       url:='https://your-project.supabase.co/functions/v1/agent-analysis',
 *       headers:='{"Content-Type": "application/json", "Authorization": "Bearer YOUR_ANON_KEY"}'::jsonb,
 *       body:='{}'::jsonb
 *     ) AS request_id;
 *   $$
 * );
 */

serve(async (req) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // For security, verify this is a cron job or has proper auth
    const authHeader = req.headers.get('Authorization')
    const cronSecret = Deno.env.get('CRON_SECRET')

    // Allow either cron secret or anon key
    if (cronSecret && authHeader !== `Bearer ${cronSecret}`) {
      const anonKey = Deno.env.get('SUPABASE_ANON_KEY')
      if (authHeader !== `Bearer ${anonKey}`) {
        return new Response(
          JSON.stringify({ error: 'Unauthorized' }),
          { status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        )
      }
    }

    const supabase = createServiceClient()

    // Get all active subscriptions with agent info
    const { data: subscriptions, error: subError } = await supabase
      .from('user_agent_subscriptions')
      .select(`
        id,
        user_id,
        agent_id,
        config,
        agents (
          id,
          name,
          role,
          description,
          data_sources,
          trigger_conditions
        )
      `)
      .eq('is_active', true)
      .eq('agents.is_active', true)

    if (subError || !subscriptions || subscriptions.length === 0) {
      return new Response(
        JSON.stringify({
          message: 'No active subscriptions found',
          processed: 0
        }),
        { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    console.log(`Processing ${subscriptions.length} subscriptions`)

    // Group by agent to avoid duplicate analysis
    const agentGroups = new Map<string, any[]>()

    for (const sub of subscriptions) {
      const agentId = sub.agent_id
      if (!agentGroups.has(agentId)) {
        agentGroups.set(agentId, [])
      }
      agentGroups.get(agentId)!.push(sub)
    }

    let alertsCreated = 0

    // Process each agent
    for (const [agentId, agentSubs] of agentGroups.entries()) {
      const agent = agentSubs[0].agents

      console.log(`Analyzing agent: ${agent.name} (${agent.role})`)

      try {
        // TODO: Here you would implement actual data fetching and analysis
        // For now, this is a mock implementation

        // Example: Analyze based on agent role
        let analysisResult = null

        if (agent.role === 'dev_efficiency_analyst') {
          analysisResult = await analyzeDevelopmentEfficiency(agent, supabase)
        } else if (agent.role === 'nps_analyst') {
          analysisResult = await analyzeNPS(agent, supabase)
        }
        // Add more agent types as needed

        // If analysis found something noteworthy, create alerts
        if (analysisResult && analysisResult.shouldAlert) {
          // Save analytics record
          await supabase.from('agent_analytics').insert({
            agent_id: agentId,
            analysis_date: new Date().toISOString().split('T')[0],
            analysis_period: 'hourly',
            data: analysisResult.data,
            insights: analysisResult.insights,
            anomalies: analysisResult.anomalies,
            alerts_generated: agentSubs.length,
          })

          // Create alerts for each subscribed user
          for (const sub of agentSubs) {
            if (sub.config?.notify_on_alert !== false) {
              await supabase.from('alerts').insert({
                agent_id: agentId,
                user_id: sub.user_id,
                title: analysisResult.title,
                description: analysisResult.description,
                severity: analysisResult.severity,
                data: analysisResult.data,
              })
              alertsCreated++
            }
          }
        }
      } catch (error) {
        console.error(`Error analyzing agent ${agent.name}:`, error)
      }
    }

    return new Response(
      JSON.stringify({
        success: true,
        subscriptions_processed: subscriptions.length,
        agents_analyzed: agentGroups.size,
        alerts_created: alertsCreated,
      }),
      { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )

  } catch (error) {
    console.error('Error in agent-analysis:', error)
    return new Response(
      JSON.stringify({ error: error.message }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }
})

/**
 * Analyze development efficiency metrics
 * Mock implementation - replace with actual data fetching
 */
async function analyzeDevelopmentEfficiency(agent: any, supabase: any) {
  // TODO: Fetch real data from Gerrit, Jira, etc.
  // This is a mock implementation

  const mockData = {
    review_time_median: 25, // hours
    review_time_p95: 48,
    reviews_pending: 12,
    reviews_completed: 45,
  }

  // Check trigger conditions
  const conditions = agent.trigger_conditions || {}
  const threshold = conditions.review_time_threshold || 24

  if (mockData.review_time_median > threshold) {
    return {
      shouldAlert: true,
      title: '代码Review耗时异常上涨',
      description: `最近代码Review的中位耗时达到${mockData.review_time_median}小时，超过阈值${threshold}小时。可能影响开发节奏。`,
      severity: 'warning',
      data: mockData,
      insights: {
        trend: 'increasing',
        impact: 'medium',
        recommendation: '建议检查是否有复杂需求导致，或团队负载过高'
      },
      anomalies: [{
        metric: 'review_time_median',
        value: mockData.review_time_median,
        threshold: threshold,
        deviation: ((mockData.review_time_median - threshold) / threshold * 100).toFixed(1) + '%'
      }]
    }
  }

  return null
}

/**
 * Analyze NPS metrics
 * Mock implementation
 */
async function analyzeNPS(agent: any, supabase: any) {
  // TODO: Fetch real NPS data
  const mockData = {
    nps_score: 35,
    promoters: 45,
    passives: 35,
    detractors: 20,
    total_responses: 100,
  }

  const conditions = agent.trigger_conditions || {}
  const threshold = conditions.nps_threshold || 40

  if (mockData.nps_score < threshold) {
    return {
      shouldAlert: true,
      title: 'NPS分数低于预期',
      description: `当前NPS分数为${mockData.nps_score}，低于目标值${threshold}。需要关注用户反馈。`,
      severity: 'warning',
      data: mockData,
      insights: {
        trend: 'declining',
        impact: 'high',
        recommendation: '建议深入分析负面反馈原因'
      },
      anomalies: [{
        metric: 'nps_score',
        value: mockData.nps_score,
        threshold: threshold,
        deviation: ((mockData.nps_score - threshold) / threshold * 100).toFixed(1) + '%'
      }]
    }
  }

  return null
}
