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

  // --- YOUR CHAT WINDOW INJECTION ---
  const menuPopup = win.document.getElementById('menu_ToolsPopup');
  if (menuPopup) {
      const menuItem = win.document.createElementNS('http://www.mozilla.org/keymaster/gatekeeper/there.is.only.xul', 'menuitem');
      menuItem.setAttribute('label', 'Open Library Assistant');
      
      menuItem.addEventListener('command', () => {
          // This opens your chat.html file in a new popup window
          win.open(
              'chrome://locallibraryassistant/content/chat.html', 
              'LibraryAssistantChat', 
              'chrome,centerscreen,width=450,height=550'
          );
      });
      
      menuPopup.appendChild(menuItem);
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
