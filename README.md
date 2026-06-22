---

# **SourceOps - ReOpped**

**SourceOps ReOpped** is a technical overhaul of the original SourceOps toolset for Blender. This version, remade and optimized by **LESSMAN**, automates the most tedious parts of the Source 1 pipeline—handling textures, physics, and complex QC configurations directly within Blender.

**Compatibility:** Blender 2.83 through 4.2+.

---

## **Technical Enhancements**

### **1. Automated Texture & Material Pipeline**
*   **Integrated Conversion:** Powered by **MareTF**, ReOpped extracts and converts Blender textures into VTF format automatically during export.
*   **Smart VMT Logic:** Automatically generates `.vmt` files while **preserving manual code edits**. If you modify a VMT in a text editor, ReOpped respects your overrides on future exports.
*   **Alpha & Normal Mapping:** Includes automated **Alpha Baking** from BSDF sliders and 1-click **Normal Map** (`_normalmap`) generation.

### **2. Native V-HACD Integration**
*   **Precision Physics:** Direct implementation of the **V-HACD** algorithm to generate optimized convex hulls for Source physics meshes.
*   **Automated Cleanup:** Generated hulls are automatically renamed, shaded smooth, and moved to specific collision collections.

### **3. Advanced LOD & QC Automation**
*   **6-Level LOD System:** Dedicated UI for managing **LOD 1 through LOD 6** collections and distances.
*   **QC Writing:** Automatically writes `$cdmaterials`, `$modelname`, `$lod` blocks, and bodygroup syntax, removing the need for manual text editing.

### **4. Environment & Tooling**
*   **Path Persistence:** Features an **Auto-Restore** system. All game paths and preferences are backed up to JSON and reloaded instantly when Blender starts.
*   **Scale Reference:** 1-click spawn of an **info_playerstart** reference model for accurate world-scale modeling.
*   **Modern Compilers:** Built-in hooks for community tools like **HLMV++** and **StudioMDL++**.

---

## **Tutorial: Generating Collisions**

To create an accurate physics mesh for your model:
1.  **Select your object** in the 3D Viewport.
2.  Press **F3** and search for: `SourceOps Collision`. (Alternatively, go to the **Object** menu at the top and find the **SourceOps ReOpped Collision Menu**).
3.  In the V-HACD popup menu, adjust the **Maximum Concavity**:
    *   **Set to 0:** For the most detailed and accurate collision mesh (creates more hulls).
    *   **Set to 1:** For the simplest possible collision mesh (fewer hulls).
    *   Adjust between **0 and 1** until the collision matches your needs.

---

## **Installation**

1.  Download **Blender 2.83 or newer**: https://www.blender.org/download/
2.  Download the **SourceOps ReOpped .zip**. **(Do not unzip the release).**
3.  In Blender, navigate to **Edit > Preferences > Add-ons**.
4.  Click **Install...**, select the `.zip` file, and enable **Import-Export: SourceOps ReOpped**.
5.  **Linux / Steam Deck:** Specify your **Wine** binary path in the addon preferences to run the Windows compilers.

---

## **Integrated Components**

This remake integrates and utilizes the following third-party tools:
*   **MareTF (Texture Conversion):** https://github.com/craftablescience/MareTF
*   **V-HACD (Collision Generation):** https://github.com/kmammou/v-hacd
*   **X3D Importer:** Native integration for processing physics data.

---

## **Workflow**

1.  **Game Setup:** Add your game folder (containing `gameinfo.txt`) in the **Games** panel.
2.  **Asset Setup:** Use **"Add Collections"** in the **Models** panel to batch-populate the export list.
3.  **VMT Overrides:** Use the **"Preview / Edit VMT"** button to open the shader code in Blender's Text Editor for custom overrides.
4.  **Export:** Click the **Auto Export** icon (Magic Wand/Car icon) to run the full pipeline.
    *   **Pro Tip:** **Hold CTRL + Left Click** on the Export icon to open a dialog with advanced options, allowing you to toggle specific export steps.

---

## **Credits**

**SourceOps ReOpped** is maintained by **LESSMAN**.

This project is a technical remake of the original SourceOps by **bonjorno7** and the community:
https://github.com/bonjorno7/SourceOps

**Original Authors & Contributors:**
bonjorno7, CabbageMcGravel, GorangeNinja, JonasAlmaas, KrystianoXPL, Peak-CDE, REDxEYE, SethTooQuick, VortexParadox, xchellx, Horiuchi.

---

## **Support**

To support the original development of the SourceOps base, visit:
[Gumroad](https://bonjorno7.gumroad.com) or [Blender Market](https://blendermarket.com/creators/bonjorno7).
[PayPal](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=43R2CKWLJZ78S).