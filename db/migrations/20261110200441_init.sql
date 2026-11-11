-- migrate:up

create table status_checks (
    id uuid primary key default gen_random_uuid(),
    hostname text not null,
    success bool not null,
    reboot bool not null,
    uptime interval not null,
    created_at timestamptz not null default now()
);

-- migrate:down

drop table status_checks

