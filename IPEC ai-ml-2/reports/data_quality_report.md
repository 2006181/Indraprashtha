# Data Quality & Health Validation Report
## Summary
- **Total Datasets Validated**: 5
- **Total Issues Identified**: 4

## Dataset Details
### etrain_delays.csv
- **Row Count**: 1900
- **Col Count**: 11
- **Unique Trains**: 90
- **Unique Stations**: 480
- **Duplicate Rows**: 0
- **Issues Count**: 1
- **Issues Identified**:
  - ⚠️ Missing average_delay_minutes in 236 rows.

### Train_delay_Prediction.csv
- **Row Count**: 190
- **Col Count**: 4
- **Duplicate Rows**: 0
- **Issues Count**: 1
- **Issues Identified**:
  - ⚠️ Missing 'Started On' timestamp in 2 rows.

### india_railway_stations
- **Row Count**: 8990
- **Unique Stations**: 8990
- **Junction Count**: 4112
- **Duplicate Rows**: 0
- **Issues Count**: 1
- **Issues Identified**:
  - ⚠️ Missing coordinates for 189 stations.

### train_schedules_json
- **Total Trains**: 8490
- **Express Trains**: 2533
- **Passenger Trains**: 4545
- **Superfast Trains**: 1412
- **Total Route Leg Stops**: 170340
- **Empty Routes**: 0
- **Issues Count**: 0
- **Status**: ✅ Clean / Valid

### Railway_Scheduling_Data.xlsx
- **Row Count**: 100
- **Columns**: ['id', 'name', 'route', 'type', 'status', 'speed_kmh', 'delay_minutes', 'priority', 'from_station', 'to_station', 'lat', 'lng']
- **Issues Count**: 1
- **Issues Identified**:
  - ⚠️ Found 12 trains with speed <= 0.
