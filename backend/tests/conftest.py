import os

TEST_ENV = {
    "SUPABASE_URL": "https://example.supabase.co",
    "SUPABASE_ANON_KEY": "anon-key",
    "SUPABASE_SERVICE_ROLE_KEY": "service-role-key",
    "DATABASE_URL": "postgresql://postgres:password@db.example.supabase.co/postgres",
    "OPENAI_API_KEY": "openai-key",
    "ALLOWED_ORIGINS": "http://localhost:5173",
}

for name, value in TEST_ENV.items():
    os.environ.setdefault(name, value)
