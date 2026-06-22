
---

# **SourceOps - ReOpped**

**SourceOps ReOpped** is a massive overhaul of the original SourceOps toolset for Blender. I remade and optimized this version to kill the manual bottlenecks in the Source 1 pipeline—specifically automating textures, collisions, and complex QC setups so you don't have to spend half your time in a text editor.

**Compatibility:** Blender 2.83 all the way up to 4.2+.

---

## **New Features & Overhauls**

### **1. Automated Texture & Material Pipeline**
*   **Native Conversion:** Powered by **MareTF**. ReOpped extracts and converts your Blender textures into VTF format automatically when you export.
*   **Smart VMTs:** It generates your `.vmt` files for you but **it won't wipe your manual work**. If you edit a VMT in a text editor, ReOpped is smart enough to preserve those changes on the next export.
*   **Alpha & Normal Maps:** You get automated **Alpha Baking** (pulled directly from your Blender BSDF sliders) and 1-click **Normal Map** (`_normalmap`) generation.

### **2. Native V-HACD Collisions**
*   **Built-in Physics:** I integrated the **V-HACD** algorithm directly. You can generate optimized convex hulls for your physics meshes without leaving Blender.
*   **Auto-Cleanup:** It automatically renames the hulls, shades them smooth, and moves them into a dedicated collision collection for you.

### **3. LOD & QC Automation**
*   **6-Level LOD System:** A full UI to manage **LOD 1 through LOD 6** collections and distances.
*   **No more manual QC editing:** ReOpped writes your `$cdmaterials`, `$modelname`, `$lod` blocks, and bodygroup syntax for you.

### **4. Better Tooling**
*   **Auto-Restore:** Your game paths and preferences are backed up to a JSON file. Every time you open Blender, they are reloaded instantly.
*   **Modern Compilers:** Built-in support for community tools like **HLMV++** and **StudioMDL++**.
*   **Scale Reference:** A button to instantly spawn an **info_playerstart** model so you don't mess up your prop scale.

---

## **Tutorial: How to make Collisions**

If you need a physics mesh that actually fits your model:
1.  **Select your object** in the viewport.
2.  Press **F3** and search for `SourceOps Collision` (or find it in the **Object** menu at the top).
3.  In the V-HACD menu, look for **Maximum Concavity**:
    *   **Set it to 0:** Most detailed/accurate (creates more hulls).
    *   **Set it to 1:** Simplest/fastest (creates fewer hulls).
    *   Find a balance in between that looks good for your model.

---

## **Installation**

1.  Grab **Blender 2.83 or newer**: https://www.blender.org/download/
2.  Download the **SourceOps ReOpped .zip**. **Do NOT unzip it.**
3.  Inside Blender, go to **Edit > Preferences > Add-ons**.
4.  Click **Install...**, pick the `.zip`, and enable **Import-Export: SourceOps ReOpped**.
5.  **Linux / Steam Deck Users:** You need to set your **Wine** path in the addon preferences to use the compilers.

---

## **How to Export**

Just click the **Auto Export** icon (the one with the car/magic wand). It runs the whole chain: Mesh > Textures > QC > Compile > View.

**PRO TIP:** **Hold CTRL + Left Click** on the Export icon to open a hidden menu. You can toggle specific steps on or off if you only want to re-compile the model or only export textures.

---

## **Integrated Tools**

This addon wouldn't work without these great projects:
*   **MareTF (Texture Conversion):** https://github.com/craftablescience/MareTF
*   **V-HACD (Collision Algorithm):** https://github.com/kmammou/v-hacd
*   **X3D Importer:** Used for native physics data processing.

---

## **Shoutout**

A huge shoutout to **Glad-BR** for the massive help with the Linux integration. They did the heavy lifting to make **MareTF** work natively on Linux for this version.
Check them out: https://github.com/Glad-BR

---

## **Credits**

**SourceOps ReOpped** is maintained by **LESSMAN**.

The original tool was built by **bonjorno7** and their contributors:
https://github.com/bonjorno7/SourceOps

**Original Team:**
bonjorno7, CabbageMcGravel, GorangeNinja, JonasAlmaas, KrystianoXPL, Peak-CDE, REDxEYE, SethTooQuick, VortexParadox, xchellx, Horiuchi.

---

## **Special Thanks**

Special thanks to the **SourceIO** and **SourceOps** Discord communities for the testing and feedback during development.

---

## **Support The Original Creator of SourceOps**

[Gumroad](https://bonjorno7.gumroad.com) or [Blender Market](https://blendermarket.com/creators/bonjorno7).
[PayPal](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=43R2CKWLJZ78S).