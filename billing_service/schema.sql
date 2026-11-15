create table if not exists public.lm_profiles (
  user_id uuid primary key,
  email text not null,
  trial_started_at timestamptz not null default now(),
  access_expires_at timestamptz,
  plan_label text
);

create table if not exists public.lm_orders (
  order_id text primary key,
  user_id uuid not null references public.lm_profiles(user_id),
  plan_id text not null,
  plan_label text not null,
  amount_paise integer not null,
  duration_days integer not null,
  status text not null default 'created',
  payment_id text unique,
  created_at timestamptz not null default now()
);

alter table public.lm_profiles enable row level security;
alter table public.lm_orders enable row level security;
revoke all on public.lm_profiles, public.lm_orders from anon, authenticated;

create or replace function public.complete_lm_payment(p_order_id text, p_payment_id text)
returns boolean
language plpgsql
security definer
set search_path = ''
as $$
declare
  paid_order public.lm_orders%rowtype;
begin
  update public.lm_orders
  set status = 'paid', payment_id = p_payment_id
  where order_id = p_order_id and status = 'created' and payment_id is null
  returning * into paid_order;
  if not found then
    return false;
  end if;
  update public.lm_profiles
  set access_expires_at = greatest(coalesce(access_expires_at, now()), now()) + make_interval(days => paid_order.duration_days),
      plan_label = paid_order.plan_label
  where user_id = paid_order.user_id;
  return true;
end;
$$;

revoke all on function public.complete_lm_payment(text, text) from public, anon, authenticated;
grant execute on function public.complete_lm_payment(text, text) to service_role;

notify pgrst, 'reload schema';

