import { getString, initLocale } from "./utils/locale";
import { registerPrefsScripts } from "./modules/preferenceScript";
import { createZToolkit } from "./utils/ztoolkit";

async function onStartup() {
  await Promise.all([
    Zotero.initializationPromise,
    Zotero.unlockPromise,
    Zotero.uiReadyPromise,
  ]);

  initLocale();

  await Promise.all(
    Zotero.getMainWindows().map((win) => onMainWindowLoad(win)),
  );

  addon.data.initialized = true;
}

async function onMainWindowLoad(win: _ZoteroTypes.MainWindow): Promise<void> {
  addon.data.ztoolkit = createZToolkit();

  win.MozXULElement.insertFTLIfNeeded(
      `${addon.data.config.addonRef}-mainWindow.ftl`,
  );

  // Chat window injection
  const menuPopup = win.document.getElementById('menu_ToolsPopup');
  if (menuPopup) {
      const menuItem = win.document.createElementNS('http://www.mozilla.org/keymaster/gatekeeper/there.is.only.xul', 'menuitem');
      menuItem.setAttribute('label', 'Open Library Assistant');

      menuItem.addEventListener('command', () => {
        win.openDialog(
            'chrome://locallibraryassistant/content/chat.html',
            'LibraryAssistantChat',
            'chrome,titlebar,toolbar,centerscreen,resizable=yes,scrollbars=yes,width=450,height=550'
        );
      });
    menuPopup.appendChild(menuItem);
  }

  // Ingestion pipeline
  const itemMenu = win.document.getElementById('zotero-itemmenu');
  if (itemMenu) {
    const rightClickItem = win.document.createElementNS('http://www.mozilla.org/keymaster/gatekeeper/there.is.only.xul', 'menuitem');
    rightClickItem.setAttribute('label', 'Send to Local Library Assistant');

    rightClickItem.addEventListener('command', async () => {
      // Get the currently selected paper
      const items = win.ZoteroPane.getSelectedItems();
      if (!items || items.length === 0) return;

      const item = items[0];
      let attachment = item;

      // If they clicked the parent container, search inside it for the PDF
      if (item.isRegularItem()) {
        const attachmentIDs = item.getAttachments();
        for (const id of attachmentIDs) {
          const att = Zotero.Items.get(id);
          if (att.attachmentContentType === 'application/pdf') {
            attachment = att;
            break;
          }
        }
      }

      if (!attachment || attachment.attachmentContentType !== 'application/pdf') {
        win.alert("Please select a PDF file or an item that contains a PDF.");
        return;
      }

      try {
        win.alert("Processing PDF... sending to local backend.");

        // 1. Get the physical file path on the Linux machine
        const filePath = await attachment.getFilePathAsync();
        if (!filePath) throw new Error("Could not locate file path.");

        // 2. Read the binary file into memory
        const fileURL = 'file://' + filePath;
        const fileReq = await win.fetch(fileURL);
        const blob = await fileReq.blob();

        // 3. Package it into a multipart form (just like Postman/cURL)
        const formData = new win.FormData();
        formData.append('file', blob, attachment.getField('title') + ".pdf");

        // 4. Fire it to your API Gateway
        const response = await win.fetch('http://localhost:8000/upload', {
          method: 'POST',
          body: formData
        });

        if (response.ok) {
          const data = await response.json();
          win.alert("Success! Saga transaction complete. " + data.chunks_saved + " text chunks were saved to ChromaDB.");
        } else {
          win.alert("Gateway Error: " + response.statusText);
        }
      } catch (error) {
        win.alert("Upload failed: " + error.message);
      }
    });

    itemMenu.appendChild(rightClickItem);
  }
}

async function onMainWindowUnload(win: Window): Promise<void> {
  ztoolkit.unregisterAll();
  addon.data.dialog?.window?.close();
}

function onShutdown(): void {
  ztoolkit.unregisterAll();
  addon.data.dialog?.window?.close();
  addon.data.alive = false;
  // @ts-expect-error - Plugin instance is not typed
  delete Zotero[addon.data.config.addonInstance];
}

async function onNotify(event: string, type: string, ids: Array<string | number>, extraData: { [key: string]: any }) {
  return;
}

async function onPrefsEvent(type: string, data: { [key: string]: any }) {
  if (type === "load") {
    registerPrefsScripts(data.window);
  }
}

function onShortcuts(type: string) { return; }
function onDialogEvents(type: string) { return; }

export default {
  onStartup,
  onShutdown,
  onMainWindowLoad,
  onMainWindowUnload,
  onNotify,
  onPrefsEvent,
  onShortcuts,
  onDialogEvents,
};
