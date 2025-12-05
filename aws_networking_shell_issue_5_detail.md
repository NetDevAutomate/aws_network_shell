# AWS Networking Shell Issue 5 Detail

## Issue Description
The TGW Route Table details view was missing critical information regarding **Associations** and **Propagations**. While the tool could list route tables and routes, it did not show which attachments were associated with or propagating to a specific route table.

## Fix Implementation
1.  **Backend (`src/aws_network_tools/modules/tgw.py`)**:
    - Updated `TGWClient._scan_region` to make additional API calls:
        - `get_transit_gateway_route_table_associations`
        - `get_transit_gateway_route_table_propagations`
    - Stored the results in the `route_tables` dictionary structure under `associations` and `propagations` keys.

2.  **Frontend (`src/aws_network_tools/modules/tgw.py`)**:
    - Updated `TGWDisplay.show_route_table` to render two new tables:
        - **Associations**: Shows Attachment ID, Resource ID, Type, and State.
        - **Propagations**: Shows Attachment ID, Resource ID, Type, and State.
    - These tables appear below the existing Routes table if data is present.

## Verification
- Created a new test file `tests/test_issue_5_tgw_rt_details.py`.
- Mocked the AWS EC2 API responses for TGWs, Attachments, Route Tables, Routes, Associations, and Propagations.
- Verified that `TGWClient` correctly populates the new fields.
- **Test Result**: PASSED

## Files Modified
- `src/aws_network_tools/modules/tgw.py`
- `tests/test_issue_5_tgw_rt_details.py` (New test file)
