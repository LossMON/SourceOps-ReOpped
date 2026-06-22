
---

# **SourceOps - ReOpped**

**SourceOps ReOpped** is a production-focused remake of the original SourceOps toolset for Blender. Remade and optimized by **LESSMAN**, this version is built to handle the most annoying parts of the Source 1 pipeline automatically—specifically texture conversion, optimized collisions, and complex QC configurations.

**Compatibility:** Blender 2.83 through 4.2+.

---

## **New Stuff & Big Changes**

### **1. Automated Texture Pipeline**
*   **Built-in Conversion:** ReOpped uses **MareTF** to handle the extraction and conversion of Blender textures into VTF format during the export process.
*   **Smart VMT Logic:** Automatically writes `.vmt` files but **preserves your manual code edits**. If you’ve added custom parameters in a text editor, ReOpped won't overwrite them on your next export.
*   **Alpha Baking:** Your Blender BSDF alpha slider values are baked directly into the VTF pixels during conversion.
*   **Normal Maps:** 1-click generation and linking for `_normalmap` files based on your material nodes.

### **2. Native V-HACD Integration**
*   **Optimized Physics:** Uses the **V-HACD** algorithm to generate accurate convex hulls for Source physics meshes without leaving Blender.
*   **Auto-Cleanup:** Hulls are automatically renamed, shaded smooth, and organized into specific collision collections.

### **3. Advanced LOD & QC Automation**
*   **6-Level LOD System:** A full UI for managing **LOD 1 through LOD 6** collections and distances.
*   **Hands-off QC Writing:** The addon writes all `$cdmaterials`, `$modelname`, `$lod` blocks, and bodygroup syntax for you.

### **4. Persistence & Tooling**
*   **Auto-Restore:** All game paths and preferences are backed up to a JSON file and reloaded automatically when Blender is launched.
*   **Modern Compilers:** Full support for **HLMV++** and **StudioMDL++**.
*   **Scale Reference:** A button to spawn an **info_playerstart** reference model to ensure your prop isn't huge or tiny in-game.

---

## **Tutorial: Generating Collisions**

To create an accurate physics mesh for your model:
1.  **Select your object** in the 3D Viewport.
2.  Press **F3** and search for: `SourceOps Collision`. (Or go to the **Object** menu at the top and find **SourceOps ReOpped Collision Menu**).
3.  In the popup menu, look for **Maximum Concavity**:
    *   **Set it to 0:** For the most detailed and accurate collision mesh (creates more hulls).
    *   **Set it to 1:** For the simplest possible collision mesh (fewer hulls/one big hull).
    *   Adjust the number between 0 and 1 until the red hulls match the shape of your mesh.

---

## **Workflow Tips**

*   **Game Setup:** Add your game folder (containing `gameinfo.txt`) in the **Games** panel. ReOpped auto-resolves your compiler and modelsrc paths.
*   **VMT Overrides:** Use the **"Preview / Edit VMT"** button to open the shader code in Blender's Text Editor for custom overrides.
*   **Smart Export:** Click the **Auto Export** icon to run the whole pipeline (Mesh > Textures > QC > Compile > View).
*   **Hidden Menu:** **Hold CTRL + Left Click** on the Export icon to open a dialog where you can toggle specific steps, like skipping the texture export or the compile step.

---

## **Installation**

1.  Download **Blender 2.83 or newer**: https://www.blender.org/download/
2.  Download the **SourceOps ReOpped .zip**. **(Do not unzip the file).**
3.  In Blender, go to **Edit > Preferences > Add-ons**.
4.  Click **Install...**, select the `.zip`, and enable **Import-Export: SourceOps ReOpped**.
5.  **Linux / Steam Deck Users:** You must specify your **Wine** binary path in the addon preferences to run the Windows compilers.

---

## **Integrated Tools**

ReOpped utilizes these third-party tools to handle the heavy lifting:
*   **MareTF (Texture Conversion):** https://github.com/craftablescience/MareTF
*   **V-HACD (Collision Generation):** https://github.com/kmammou/v-hacd
*   **X3D Importer:** Native integration for processing physics data.

---

## **Credits & Shoutouts**

| **Project Credits** | **Special Thanks & Shoutouts** |
| :--- | :--- |
| **LESSMAN** - Remake, optimization, and new features. | **Glad-BR** - For the specialized work making MareTF work natively on Linux in this version. (https://github.com/Glad-BR) |
| **bonjorno7** - Original SourceOps creator. (https://github.com/bonjorno7/SourceOps) | **V-HACD** - Algorithm by Khaled Mamou and Alain Ducharme. |
| **Original Contributors:** CabbageMcGravel, GorangeNinja, JonasAlmaas, KrystianoXPL, Peak-CDE, REDxEYE, SethTooQuick, VortexParadox, xchellx, Horiuchi. | |

---

## **Support**

To support the original development of the SourceOps base, visit:
[Gumroad](https://bonjorno7.gumroad.com) or [Blender Market](https://blendermarket.com/creators/bonjorno7).
[PayPal](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=43R2CKWLJZ78S).