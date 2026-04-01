# 🎯 Life OS - Personal Command Center

A minimalist Streamlit application for tracking wealth, health, and daily expenses with AI-powered features.

![Life OS Dashboard](https://via.placeholder.com/800x400?text=Life+OS+Dashboard)

## Features

- **💰 Finance Hub**: Track Nasdaq-100 DCA investments with real-time pricing via yfinance
- **🧾 AI Receipt Scanner**: Upload/photograph receipts and extract data using Google Gemini
- **💪 Health Tracker**: Log Evolt 360 body composition data with AI-powered report scanning
- **📊 Dashboard**: Combined life progress visualization with claymorphism UI design

## Prerequisites

- Python 3.9+
- Supabase account (free tier works)
- Google AI Studio API key (for Gemini)
- GitHub account (for Streamlit Cloud deployment)

## Supabase Setup

### 1. Create a New Project

1. Go to [supabase.com](https://supabase.com) and create a new project
2. Note your **Project URL** and **anon public key** from Settings > API

### 2. Create Database Tables

Run these SQL commands in the Supabase SQL Editor:

```sql
-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- Ledger table for expenses
create table public.ledger (
    id uuid default uuid_generate_v4() primary key,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    amount decimal(10,2) not null,
    category text not null,
    note text default '',
    image_url text
);

-- Physical stats table for health tracking
create table public.physical_stats (
    id uuid default uuid_generate_v4() primary key,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    body_fat_pct decimal(5,2),
    muscle_mass decimal(5,2),
    visceral_fat decimal(5,2)
);

-- Investments table for portfolio tracking
create table public.investments (
    id uuid default uuid_generate_v4() primary key,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    symbol text not null default 'NDX',
    purchase_price decimal(10,4) not null,
    quantity decimal(12,6) not null,
    total_invested decimal(12,2) not null
);

-- Create indexes for better performance
create index idx_ledger_created_at on public.ledger(created_at desc);
create index idx_ledger_category on public.ledger(category);
create index idx_physical_stats_created_at on public.physical_stats(created_at desc);
create index idx_investments_created_at on public.investments(created_at desc);
create index idx_investments_symbol on public.investments(symbol);

-- Enable Row Level Security (optional but recommended)
alter table public.ledger enable row level security;
alter table public.physical_stats enable row level security;
alter table public.investments enable row level security;

-- Create policies to allow authenticated access (adjust as needed)
create policy "Allow all operations on ledger" on public.ledger
    for all using (true) with check (true);

create policy "Allow all operations on physical_stats" on public.physical_stats
    for all using (true) with check (true);

create policy "Allow all operations on investments" on public.investments
    for all using (true) with check (true);
```
