
---

# **SourceOps - ReOpped**

**SourceOps ReOpped** is a production-ready overhaul of the original SourceOps toolset for Blender. This version, remade and optimized by **LESSMAN**, focuses on eliminating the manual bottlenecks of the Source 1 pipeline by automating texture conversion, collision generation, and complex QC configurations.

**Compatibility:** Blender 2.83 through 4.2+.

---

## **Technical Enhancements & New Features**

### **1. Automated Texture & Material Pipeline**
*   **Integrated Conversion:** Powered by **MareTF**, ReOpped handles the direct extraction and conversion of Blender textures into VTF format during export.
*   **Smart VMT Logic:** Automatically generates `.vmt` files while **preserving manual code edits**. If you modify a VMT in a text editor, ReOpped respects those overrides on subsequent exports.
*   **Alpha & Normal Mapping:** Includes automated **Alpha Baking** from Blender BSDF sliders and 1-click **Normal Map** (`_normalmap`) generation.

### **2. Native V-HACD Integration**
*   **Precision Collisions:** Direct implementation of the **V-HACD** algorithm to generate optimized convex hulls for physics meshes within Blender.
*   **Automated Organization:** Hulls are automatically renamed, shaded smooth, and moved to designated collision collections.

### **3. Advanced LOD & QC Automation**
*   **6-Level LOD System:** Full UI support for managing **LOD 1 through LOD 6** collections and distances.
*   **Auto-QC Writing:** Eliminates manual text editing by automatically writing `$cdmaterials`, `$modelname`, `$lod` blocks, and bodygroup syntax.

### **4. Environment & Tooling**
*   **Path Persistence:** Features an **Auto-Restore** system. All game paths, bin directories, and preferences are backed up to JSON and reloaded automatically when Blender is launched.
*   **Compiler Support:** Dedicated hooks for modern community tools like **HLMV++** and **StudioMDL++**.
*   **Scale Reference:** 1-click spawn of an **info_playerstart** reference model for accurate world-scale modeling.

---

## **Installation**

1.  Download **Blender 2.83 or newer**: https://www.blender.org/download/
2.  Download the **SourceOps ReOpped .zip**. **(Do not unzip the release).**
3.  In Blender, navigate to **Edit > Preferences > Add-ons**.
4.  Click **Install...**, select the `.zip` file, and enable **Import-Export: SourceOps ReOpped**.
5.  **Linux / Steam Deck:** Specify your **Wine** binary path in the addon preferences to run the Windows-based compilers.

---

## **Integrated Components**

This remake integrates and utilizes the following third-party tools:
*   **MareTF (Texture Conversion):** https://github.com/craftablescience/MareTF
*   **V-HACD (Collision Generation):** https://github.com/kmammou/v-hacd
*   **X3D Importer:** Native integration for processing V-HACD output data.

---

## **Workflow**

1.  **Game Setup:** Add your game folder (containing `gameinfo.txt`) in the **Games** panel. ReOpped will auto-resolve your compiler and model paths.
2.  **Asset Setup:** Use **"Add Collections"** in the **Models** panel to batch-populate the export list from your scene collections.
3.  **Physics:** Select your mesh and use **Object > SourceOps ReOpped Collision Menu (V-HACD)** to generate a collision model.
4.  **VMT Overrides:** Use the **"Preview / Edit VMT"** button to open the shader code in Blender's Text Editor for custom overrides.
5.  **Export:** Click the **Auto Export** icon to run the pipeline (Mesh > Textures > QC > Compile > View).

---

## **Credits**

**SourceOps ReOpped** is maintained by **LESSMAN**.

This project is a fork and technical remake of the original SourceOps by **bonjorno7** and the community:
https://github.com/bonjorno7/SourceOps

**Original Authors & Contributors:**
bonjorno7, CabbageMcGravel, GorangeNinja, JonasAlmaas, KrystianoXPL, Peak-CDE, REDxEYE, SethTooQuick, VortexParadox, xchellx, Horiuchi.

---

## **Support**

To support the original development of the SourceOps base, visit:
[Gumroad](https://bonjorno7.gumroad.com) or [Blender Market](https://blendermarket.com/creators/bonjorno7).
[PayPal](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=43R2CKWLJZ78S).