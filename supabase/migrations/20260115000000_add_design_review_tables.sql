-- Design Review Tables Migration
-- Create tables for Chris Design Validator agent

-- Design reviews table
CREATE TABLE IF NOT EXISTS design_reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    designer_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    module_name VARCHAR(100),
    review_mode VARCHAR(20) CHECK (review_mode IN ('interaction', 'visual', 'comparison')),
    design_images TEXT[] NOT NULL,
    issues JSONB DEFAULT '[]'::jsonb,
    suggestions JSONB DEFAULT '[]'::jsonb,
    score DECIMAL(3,1) CHECK (score >= 0 AND score <= 10),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_design_reviews_designer ON design_reviews(designer_id);
CREATE INDEX idx_design_reviews_created_at ON design_reviews(created_at DESC);
CREATE INDEX idx_design_reviews_module ON design_reviews(module_name);
CREATE INDEX idx_design_reviews_mode ON design_reviews(review_mode);

-- RLS policies
ALTER TABLE design_reviews ENABLE ROW LEVEL SECURITY;

-- Users can read their own reviews
CREATE POLICY "Users can read own reviews"
    ON design_reviews FOR SELECT
    USING (auth.uid() = designer_id);

-- Users can insert their own reviews
CREATE POLICY "Users can insert own reviews"
    ON design_reviews FOR INSERT
    WITH CHECK (auth.uid() = designer_id);

-- Users can update their own reviews
CREATE POLICY "Users can update own reviews"
    ON design_reviews FOR UPDATE
    USING (auth.uid() = designer_id);

-- Users can delete their own reviews
CREATE POLICY "Users can delete own reviews"
    ON design_reviews FOR DELETE
    USING (auth.uid() = designer_id);

-- Create design-uploads bucket for design mockup images
INSERT INTO storage.buckets (id, name, public)
VALUES ('design-uploads', 'design-uploads', true)
ON CONFLICT (id) DO NOTHING;

-- RLS policies for design-uploads bucket
CREATE POLICY "Public read access for design uploads" ON storage.objects
FOR SELECT USING (bucket_id = 'design-uploads');

CREATE POLICY "Authenticated users can upload designs" ON storage.objects
FOR INSERT WITH CHECK (
    bucket_id = 'design-uploads'
    AND auth.role() = 'authenticated'
);

CREATE POLICY "Users can update their own design uploads" ON storage.objects
FOR UPDATE USING (
    bucket_id = 'design-uploads'
    AND auth.uid()::text = (storage.foldername(name))[1]
);

CREATE POLICY "Users can delete their own design uploads" ON storage.objects
FOR DELETE USING (
    bucket_id = 'design-uploads'
    AND auth.uid()::text = (storage.foldername(name))[1]
);

-- Comments
COMMENT ON TABLE design_reviews IS 'Design review records from Chris Design Validator';
COMMENT ON COLUMN design_reviews.designer_id IS 'User who requested the review';
COMMENT ON COLUMN design_reviews.module_name IS 'Module or feature name being reviewed';
COMMENT ON COLUMN design_reviews.review_mode IS 'Type of review: interaction, visual, or comparison';
COMMENT ON COLUMN design_reviews.design_images IS 'Array of Supabase Storage URLs for design mockup images';
COMMENT ON COLUMN design_reviews.issues IS 'JSON array of identified issues';
COMMENT ON COLUMN design_reviews.suggestions IS 'JSON array of improvement suggestions';
COMMENT ON COLUMN design_reviews.score IS 'Overall score from 0 to 10';
COMMENT ON COLUMN design_reviews.metadata IS 'Additional metadata (case references, guidelines used, etc.)';

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_design_reviews_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update updated_at
CREATE TRIGGER trigger_update_design_reviews_updated_at
BEFORE UPDATE ON design_reviews
FOR EACH ROW
EXECUTE FUNCTION update_design_reviews_updated_at();
