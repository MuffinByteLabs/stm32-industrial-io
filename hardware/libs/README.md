# Component libraries

I keep candidate footprints and mechanical models in project-relative collections. Exact component assignment and package verification are pending schematic capture.

| Collection | Contents |
| --- | --- |
| IndustrialIO.pretty | USB-C receptacle, tactile switch, 1206 fuse, SMA diode, and SOD-123F diode footprints |
| IndustrialIO.3dshapes | USB and switch STEP/VRML models |
| logos/logos.pretty | MuffinByte branding footprints |

The [native project tables](../STM32_Industrial_IO/README.md) resolve local collections through this directory. Exact pin numbering, pad geometry, exposed-pad treatment, courtyard, model alignment, and mechanical fit will be reviewed against the selected manufacturer's drawings before release.

## Attribution and license

Fuse_1206_3216Metric, D_SMA, D_SOD-123F, and USB_C_Receptacle_HRO_TYPE-C-31-M-12 are modified local copies derived from the KiCad community libraries. They were saved in KiCad 10 format, with project-local asset references where applicable. Their upstream collections are Fuse.pretty, Diode_SMD.pretty, and Connector_USB.pretty in [kicad-footprints](https://gitlab.com/kicad/libraries/kicad-footprints).

These redistributed assets retain the [KiCad Libraries License](KiCad_Library_LICENSE.md): Creative Commons Attribution-ShareAlike 4.0 with the KiCad design exception. [KiCad's licensing explanation](https://www.kicad.org/libraries/license/) distinguishes a redistributed library collection from a design using its data. The project license does not replace these terms.

KiCad_Library_LICENSE.md was downloaded unchanged from the [official upstream file](https://gitlab.com/kicad/libraries/kicad-footprints/-/raw/master/LICENSE.md) on October 2, 2026. Its SHA-256 is 45D2BCE75E5A4208F5AFB01B8FB2C406E700371C4FE2B5F5CD5C443D46DB4D8F.

The tactile-switch footprint and STEP/VRML models have incomplete original-author and redistribution-license provenance. They are not claimed as original MuffinByteLabs work or as KiCad library assets. The switch VRML retains its easyeda2kicad.py generator notice; this does not establish the source model's license. Embedded notices and source metadata remain intact. Provenance review is required before these assets are approved for the manufacturing library.
