# Blender Connection Guide

This project is configured to connect directly with your local **Blender 5.3** instance using the **Model Context Protocol (MCP)**.

---

## Connection Status: Connected & Active

- **Blender Version:** Blender 5.3.0
- **Addon Installed:** `blender_mcp` (in `~/Library/Application Support/Blender/5.3/scripts/addons/`)
- **Auto-Start Script:** `~/Library/Application Support/Blender/5.3/scripts/startup/start_blendermcp.py`
- **MCP Server Config:** `~/.gemini/config/mcp_config.json`
- **Socket Port:** `localhost:9876`

---

## How It Works

1. **Auto-Connection:** Whenever you launch Blender, the background server starts automatically on port `9876`.
2. **In-Viewport Controls:** 
   - Open Blender.
   - In the **3D Viewport**, press <kbd>N</kbd> to open the sidebar.
   - Select the **MCP for Blender** tab to see connection status, toggle the server, or adjust settings.
3. **AI Capabilities:**
   - **Scene Inspection:** Query scene objects, hierarchies, materials, and lighting.
   - **Script Execution (`bpy`):** Create procedural geometry, modify meshes, configure modifiers, assign materials, set camera angles, and animate keyframes.
   - **Viewport Capture (`look`):** Capture renders or viewport snapshots so the assistant can visually evaluate the scene.
   - **Asset Search & Import:** Search and import CC0 3D models and materials from Poly Haven, Sketchfab, etc.
