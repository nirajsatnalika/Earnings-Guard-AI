# EFS™ PHASE 6C — PEER SELECTION METHODOLOGY & SCORING

## Deterministic Peer Selection Engine

Peer selection evaluates candidate companies within the same sector using a transparent multi-factor scoring formula:

$$\text{Peer Score} = \text{Industry Score} + \text{Geography Score} + \text{Size Score} + \text{Data Availability Score}$$

### Scoring Rules
1. **Industry Match (Max 40 pts):**
   - Exact Industry Match: 40 pts
   - Same Sector: 20 pts
   - Mismatch: 0 pts (Rejected)
2. **Geography & Accounting Regime Match (Max 20 pts):**
   - Same Country & Accounting Standard (IFRS / IndAS / US GAAP): 20 pts
   - Same Region: 10 pts
3. **Revenue / Size Proximity (Max 20 pts):**
   - Revenue within $0.5\times$ to $2.0\times$ target company: 20 pts
   - Revenue within $0.2\times$ to $5.0\times$: 10 pts
4. **Data Availability (Max 20 pts):**
   - Complete multi-year financial statements & disclosures available: 20 pts

### Peer Group Quality Rules
- **Minimum Peer Count:** At least 3 peers required for a valid peer benchmark median. If $< 3$ peers available, `benchmark_status = INSUFFICIENT_PEERS`.
- **Human Overrides:** Users can confirm, edit, add, or reject candidate peers in the Human Review interface.
