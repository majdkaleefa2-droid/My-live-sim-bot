# Black Box Arbitrage Engine — V1

Professional research/paper-trading architecture for triangular crypto arbitrage.

## Important
This system is deliberately **PAPER mode by default**. No real order can be sent unless a live adapter is explicitly implemented, credentials are supplied, and all risk gates pass.

It is designed around the realities that invalidate naive arbitrage simulations:
- executable Bid/Ask rather than mid prices
- three-leg fee compounding
- spread and slippage
- latency buffer
- order-book depth / maximum executable size
- partial fills
- rejected orders
- stale market data
- circuit breakers
- daily loss limit
- maximum exposure
- maximum consecutive failures
- kill switch
- reconciliation
- immutable trade/audit logging
- walk-forward / out-of-sample research hooks

## Architecture

Market Data
    ↓
Order Book Cache
    ↓
Opportunity Engine
    ↓
Cost Model
    ↓
Risk Engine
    ↓
Execution State Machine
    ↓
Reconciliation
    ↓
Audit + Metrics

## Default philosophy

A detected edge is NOT a trade.

A trade is allowed only when:

expected_edge
- trading_fees
- spread_cost
- estimated_slippage
- latency_buffer
- safety_buffer

is greater than the required minimum edge.

The bot never assumes that three fills will occur at the same price.

## Run

Python 3.11+

Install:
    pip install -r requirements.txt

Paper simulation:
    python main.py --mode paper

Backtest:
    python main.py --mode backtest

Live mode is intentionally blocked in V1 until a venue-specific adapter has been validated.
