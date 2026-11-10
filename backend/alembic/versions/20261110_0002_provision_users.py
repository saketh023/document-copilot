"""Provision application users when Supabase accounts are created."""

from alembic import op

revision = "20261110_0002"
down_revision = "20261108_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE FUNCTION public.handle_new_auth_user()
        RETURNS trigger
        LANGUAGE plpgsql
        SECURITY DEFINER SET search_path = ''
        AS $$
        BEGIN
            INSERT INTO public.users (id) VALUES (NEW.id)
            ON CONFLICT (id) DO NOTHING;
            RETURN NEW;
        END;
        $$
    """)
    op.execute("REVOKE ALL ON FUNCTION public.handle_new_auth_user() FROM PUBLIC")
    op.execute("""
        CREATE TRIGGER on_auth_user_created
        AFTER INSERT ON auth.users
        FOR EACH ROW EXECUTE FUNCTION public.handle_new_auth_user()
    """)
    op.execute("""
        INSERT INTO public.users (id)
        SELECT id FROM auth.users
        ON CONFLICT (id) DO NOTHING
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER on_auth_user_created ON auth.users")
    op.execute("DROP FUNCTION public.handle_new_auth_user()")
