## rce-cho-mcp v0.6.0-beta

Highlights since `v0.5.0-beta`. Prompted by feedback from RCE colleagues
after a demonstration of the connector (2026-11-17). Every figure below was
counted against the live endpoints on that date.

### New

- Two new tools for separate RCE datasets, each with its own endpoint and
  schema.org vocabulary (with `verwijzingen` below: 31 tools in total, was 28):
  - `query_sparql_afbeeldingen` -- the RCE image library (Beeldbank), graph
    `.../rce/afbeeldingen/graphs/photos`: 565,170 photographs and drawings
    with image URLs, creator, date, place, licence and a link to
    rijksmonumenten via `sdo:about`
  - `query_sparql_bibliotheek` -- the RCE library catalogue, graphs
    `.../rce/bibliotheek/graphs/books` (155,422 books) and
    `.../graphs/article` (26,265 journal articles), searchable by CHT/ABR
    subject, place or rijksmonumentnummer
- New tool `verwijzingen` and resource `rce-cho://verwijzingen`: links to
  the RCE Linked Data Voorziening (frontend, SPARQL editor and SPARQL
  endpoint per dataset) and to the CEO ontology (ontology URI, namespace,
  the source file `CEO_RCE.ttl` and the version of the bundled copy). The
  same references are in a new README section (issue #29)
- Four new dataset-semantics topics: `images`, `library`,
  `formeel_standpunt` and `gemeenten`
- `graphs_list()` now also lists the graphs of these two datasets, in a
  separate section, because they do not exist on the CHO endpoint and are
  not valid as `graph_name` in `resolve_concept_label()`

### Changed behaviour

- **Formal position (`ceo:formeelStandpunt`).** Knowledge registrations
  (description, type, event/dating, style and culture, material) carry this
  boolean. By default only knowledge with `true` is shown; `false` only on
  explicit request and labelled as such. The rule is part of the server
  instructions and the `query_sparql` description, and
  `validate_query()`/`validate_query_structured()` warn when a query uses a
  mixed knowledge path (`ceo:heeftOmschrijving`, `ceo:heeftType`,
  `ceo:heeftGebeurtenis`, `ceo:heeftStijlEnCultuur`, `ceo:heeftMateriaal`,
  `ceo:heeftKennisregistratie`) without it
  - Exception, confirmed by RCE: for the archaeological classes
    `ArcheologischOnderzoeksgebied`, `Vondstlocatie`, `Vondsten`,
    `Grondsporen`, `ArcheologischTerrein` and `ArcheologischComplex` the
    boolean carries no meaning. There the connector does not filter on it,
    shows the knowledge as is, and the validator stays silent
  - The rule still applies to rijksmonumenten (including archaeological
    ones, which are `ceo:Rijksmonument` objects), complexes, protected
    townscapes and world heritage
- **Municipal mergers.** `ceo:heeftGemeente` (OWMS) has not been fully
  updated after municipal mergers: 61 abolished municipalities are still
  referenced. All 448 active rijksmonumenten of Voorne aan Zee are linked
  to its predecessor Westvoorne (Voorne aan Zee itself returned 0), 617
  delisted objects remain on 58 abolished municipalities, and archaeology
  was not updated for the mergers of 2021 through 2023
  - `monumenten_in_gemeente()` has a new parameter `inclusief_voorgangers`
    (default `True`): fully merged predecessors are counted along, with a
    breakdown per municipality. A predecessor that was split over several
    municipalities (e.g. Haaren) is never counted automatically but is
    reported separately
  - `resolve_gemeente()` now also reports whether a municipality has been
    abolished (end date and successor) and lists the URIs of its
    predecessors
  - `percelen_via_spatial_join()` translates an abolished municipality to
    its current successor before querying the Kadaster KKG, which only
    knows current municipalities -- previously a silent 0-parcel result
  - Limitation: the OWMS and TOOI graphs run up to the merger of
    2023-01-01; later mergers are not recognised

### Documentation of the data

- **Archis2 numbers.** The `archaeology` topic and the server instructions
  now state that Archis2 numbers (including
  `ceo:archis2Vondstmeldingsnummer`) are no longer issued. They only exist
  on registrations from the Archis2 era: 41,132 of the 41,514 objects with
  an `archis2Vondstmeldingsnummer` have registration date 2016 (the
  conversion), and none were added in 2023 or 2024. They are suitable for
  looking up an existing old number, not for selecting or counting "all"
  reports. The period is derived from `ceo:registratiedatum`; the exact date
  on which issuing stopped is not in the data
- **HVDL graphs.** `gezicht_hvdl` and `werelderfgoed_hvdl` now have a
  description of their actual content (area, dates, UNESCO link). This also
  corrected an error in the `geometry` topic: the WGS84 polygons of
  protected townscapes are in `instanties-rce`, not in `gezicht_hvdl` -- a
  GRAPH restriction on the latter silently returned nothing

### Housekeeping

- Test suite extended from 145 to 170 tests (predecessor selection,
  merger reporting, the formal-position warning and its archaeology
  exception, the new tools and topics)
- README, CAPABILITIES.md and the connector explainer updated to reflect
  the above

Not affiliated with the Rijksdienst voor het Cultureel Erfgoed.
