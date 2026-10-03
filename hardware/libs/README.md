# Local library assets

The retained assets support reuse while the new STM32 schematic is developed. They are candidates, not a verified BOM or approved manufacturing library.

| Directory | Contents and status |
| --- | --- |
| IndustrialIO.pretty | USB-C receptacle, tactile switch, 1206 fuse, SMA diode, and SOD-123F diode footprints retained for possible reuse |
| IndustrialIO.3dshapes | USB/switch mechanical models matching the retained footprint references |
| logos/logos.pretty | MuffinByte branding footprints |

The USB/switch source drawings remain in [references/datasheets/](../../references/datasheets/README.md). Verify exact component identity, dimensions, pin numbering, courtyard, pad/paste geometry, and mating fit before assigning any of these assets. An old distributor identifier embedded in a retained filename describes that asset's provenance, rather than a new board purchasing decision.

Project tables live in [hardware/STM32_Industrial_IO/](../STM32_Industrial_IO/README.md). Project-relative model paths use the parent libs directory; stock KiCad models use the installed KiCad model variable.

Add new symbols, footprints, and models only after exact package verification. Store a review record with source drawing, reviewer/date, pin-pad checks, and unresolved assumptions. Imported assets and downloaded CAD require the same checks as manually created assets.

## Third-party library attribution

The retained Fuse_1206_3216Metric, D_SMA, D_SOD-123F, and USB_C_Receptacle_HRO_TYPE-C-31-M-12 footprints are modified local copies derived from the KiCad community libraries. They were saved in KiCad 10 format, with project-local asset references where applicable. Their upstream collections are Fuse.pretty, Diode_SMD.pretty, and Connector_USB.pretty in [kicad-footprints](https://gitlab.com/kicad/libraries/kicad-footprints).

These redistributed library assets retain the [KiCad Libraries License](KiCad_Library_LICENSE.md): Creative Commons Attribution-ShareAlike 4.0 with the KiCad design exception. See [KiCad's official licensing explanation](https://www.kicad.org/libraries/license/) for the distinction between a redistributed library collection and a design using its data. The project license does not replace these library terms.

KiCad_Library_LICENSE.md was downloaded unchanged from the [official upstream license file](https://gitlab.com/kicad/libraries/kicad-footprints/-/raw/master/LICENSE.md) on October 2, 2026. Its SHA-256 is 45D2BCE75E5A4208F5AFB01B8FB2C406E700371C4FE2B5F5CD5C443D46DB4D8F.

The tactile-switch footprint and the retained STEP/VRML models have incomplete original-author and redistribution-license provenance. They are not claimed as original MuffinByteLabs work or as KiCad library assets. The switch VRML retains its easyeda2kicad.py generator notice; a generator notice does not establish the source model's license. Preserve their embedded notices and source metadata, and resolve provenance before approving them for the new board's manufacturing library. MuffinByte logo footprints are project branding.
