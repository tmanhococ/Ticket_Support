# Story 11.1: Real-time Distribution Charts & Trend Monitoring

As a Support Lead,
I want to see visual charts of ticket priorities and their trends over time,
So that I can quickly assess the workload and spot any sudden spikes.

## Acceptance Criteria

1. **[AC1]** The Streamlit dashboard connects to the database and fetches the distribution of `predicted_priority` (high, medium, low).
2. **[AC2]** A time-series chart (e.g., line or area chart) is rendered on the dashboard showing the volume of incoming tickets over time, grouped by priority. This enables the user to detect sudden spikes.
3. **[AC3]** A pie chart or bar chart is also available to show the overall distribution.
4. **[AC4]** The dashboard allows viewing the most recent tickets (subjects and bodies), potentially filtered by priority, so the user can quickly identify the root cause of a spike (e.g., a "payment error").
5. **[AC5]** The charts and data update automatically or upon manual refresh to reflect real-time DB state.

## Tasks / Subtasks

- [ ] Task 1: Data Fetching & Aggregation
  - [ ] 1.1 Add a database query to count tickets grouped by `predicted_priority` and time intervals (e.g., grouped by minute or hour).
- [ ] Task 2: UI Implementation
  - [ ] 2.1 Use Streamlit (`st.line_chart`, `st.area_chart`, or Plotly) to visualize the time-series trend.
  - [ ] 2.2 Include a pie/bar chart for overall distribution.
  - [ ] 2.3 Enhance the existing ticket list (from Epic 4) to support filtering by priority or simply highlight the `high` priority tickets.

## Status

**Status:** ready-for-dev
