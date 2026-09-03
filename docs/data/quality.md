# Data Quality

Payload validation is performed before a record enters the registry. Missing
required values, invalid ranges or coordinates, negative quantities, malformed
timestamps, and invalid units produce explicit validation issues. Duplicate
`(source, source_identifier)` keys are rejected.

Rejected records are quarantined with the original raw payload/reference,
timestamp, and machine-readable issue codes; they are never silently corrected
or exposed as accepted data. The same validation function is reusable by file,
mock, and synthetic connectors.

## Forecast uncertainty

Freight forecast `p10`, `p25`, `p50`, `p75`, and `p90` values are rate
quantiles. The interval is derived from causal rolling-origin residuals at the
requested horizon. When history is insufficient, a volatility-scaled baseline
is used and the result is marked `insufficient_history`.

`model_confidence` describes forecast error performance and history volume.
`data_confidence` describes the quality scores of the input observations.
`decision_confidence` combines both and is not a business decision probability.
Calibration coverage is empirical and should be checked before using intervals
as risk limits.
