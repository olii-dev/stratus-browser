const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("electron", {
    switchTab: (index) => ipcRenderer.send("switch-tab", index),
    closeTab: (index) => ipcRenderer.send("close-tab", index),
    newTab: () => ipcRenderer.send("new-tab"),
    addTabListener: (callback) => ipcRenderer.on("add-tab", callback),
    removeTabListener: (callback) => ipcRenderer.on("remove-tab", callback)
});