# Benchmark 001: Rijksmonumenten in Zeist

## Question

Hoeveel rijksmonumenten staan in Zeist?

## Expected plan

intent: count
entity: Rijksmonument
filter:
  gemeente: Zeist

## Expected resolved values

gemeente_uri: http://standaarden.overheid.nl/owms/terms/Zeist_(gemeente)

## Expected result

180

## Notes

Only current rijksmonumenten are counted.
Uses ceo:heeftJuridischeStatus with the current rijksmonument status.
Gemeente is resolved via OWMS.