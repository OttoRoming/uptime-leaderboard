-- migrate:up

create table status_checks (
    id uuid primary key default gen_random_uuid(),
    hostname text not null,
    unreachable bool not null default false,
    reboot bool not null default false,
    uptime interval not null,
    created_at timestamptz not null default now()
);

-- migrate:down

drop table status_checks

