# Benchmark 001: Rijksmonumenten in Zeist

## Question

Hoeveel rijksmonumenten staan in Amersfoort?

## Expected plan

intent: count
entity: Rijksmonument
filter:
  gemeente: Amersfoort

## Expected resolved values

gemeente_uri: http://standaarden.overheid.nl/owms/terms/Amersfoort_(gemeente)

## Expected result

460

## Notes

Only current rijksmonumenten are counted.
Uses ceo:heeftJuridischeStatus with the current rijksmonument status.
Gemeente is resolved via OWMS.