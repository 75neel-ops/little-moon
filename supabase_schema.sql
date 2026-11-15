create table if not exists public.lm_profiles (
  user_id uuid primary key references auth.users(id) on delete cascade,
  email text not null unique,
  trial_started_at timestamptz not null default now(),
  access_expires_at timestamptz,
  plan_label text
);

create index if not exists lm_profiles_email_idx on public.lm_profiles (email);

alter table public.lm_profiles enable row level security;
revoke all on public.lm_profiles from anon, authenticated;
grant all on public.lm_profiles to service_role;

