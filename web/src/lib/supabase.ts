import { createClient } from "@supabase/supabase-js";

const SUPABASE_URL = "https://dwesyojvzbltqtgtctpt.supabase.co";
const SUPABASE_ANON_KEY =
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3ZXN5b2p2emJsdHF0Z3RjdHB0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzkzNjA3MjgsImV4cCI6MjA1NDkzNjcyOH0.O5J_kNBEudBIF35Gv-Z3sOWnXTmbxvB6bBTRS18fJmM";

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
