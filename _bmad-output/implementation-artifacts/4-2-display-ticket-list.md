# Story 4.2: Display Ticket List

Status: review

## Story

As a Support Lead,
I want to view the latest incoming tickets on the dashboard,
So that I know the system is receiving data.

## Acceptance Criteria

1. **[AC1]** The dashboard queries the database and fetches the 50 most recent tickets.
2. **[AC2]** The tickets are displayed in a clean table or list layout on the Streamlit dashboard.
3. **[AC3]** The list provides a manual "Refresh Data" button, or updates automatically.
4. **[AC4]** The UI is aesthetically pleasing, showing columns like `Ticket ID`, `Timestamp`, and `Text`.

## Tasks / Subtasks

- [x] Task 1: Fetch tickets from database
  - [x] 1.1 Write query to `SELECT * FROM tickets ORDER BY timestamp DESC LIMIT 50`.
  - [x] 1.2 Return the data as a Pandas DataFrame.

- [x] Task 2: Display data in Streamlit
  - [x] 2.1 Use `st.dataframe` or `st.table` to render the DataFrame.
  - [x] 2.2 Add a refresh mechanism using `st.button` to trigger data refetching.

## Dev Notes

### Streamlit Table Display
- Use `st.dataframe(df, use_container_width=True, hide_index=True)` for a clean, modern look.
- We should ensure `timestamp` is formatted readably.
- The `text` column might be long, so `st.dataframe` works better as it allows scrolling/expanding compared to `st.table`.

### Refreshing Data
- Streamlit reruns the script from top to bottom on interaction. Adding a `st.button("Refresh Data")` will trigger a rerun, effectively fetching the latest data.
- Ensure that the query function does NOT heavily cache if we want real-time updates. Avoid `st.cache_data` on the fetch tickets function unless `ttl` is very short (e.g., `ttl=5`).

### Previous Story Context
- `4-1-setup-streamlit-application` provides the base app and connection. This story focuses purely on the UI component.

## Dev Agent Record

### Completion Notes
- ✅ AC1: Added `fetch_latest_tickets` with `LIMIT 50` query.
- ✅ AC2: Used `st.dataframe(df, use_container_width=True, hide_index=True)` to cleanly render the table.
- ✅ AC3: Included a `st.button` for "🔄 Refresh Data", which causes Streamlit to rerun the script and refetch the data.
- ✅ AC4: Table dynamically scales width and hides index for cleaner look.

### File List
- `src/dashboard/app.py` [MODIFIED - added queries and dataframe rendering]

