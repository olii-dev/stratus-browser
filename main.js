const { app, BrowserWindow, BrowserView, ipcMain, globalShortcut } = require('electron');

let mainWindow;
let tabs = [];
let activeTabIndex = null;

app.whenReady().then(() => {
    mainWindow = new BrowserWindow({
        width: 1000,
        height: 700,
        titleBarStyle: 'hidden',
        frame: false,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: __dirname + "/preload.js"
        }
    });

    mainWindow.loadFile("index.html");
    createNewTab();

    ipcMain.on('switch-tab', (event, tabIndex) => {
        switchTab(tabIndex);
    });

    ipcMain.on('close-tab', (event, tabIndex) => {
        closeTab(tabIndex);
    });

    ipcMain.on('new-tab', () => {
        createNewTab();
    });

    // Register keyboard shortcuts
    globalShortcut.register('CommandOrControl+T', () => {
        createNewTab();
    });

    globalShortcut.register('CommandOrControl+W', () => {
        if (tabs.length > 1) {
            closeTab(activeTabIndex);
        } else {
            mainWindow.close(); // If only one tab is open, close the window
        }
    });

    mainWindow.on('closed', () => {
        globalShortcut.unregisterAll(); // Clean up shortcuts when window closes
    });

    globalShortcut.register('CommandOrControl+<', () => {
    if (tabs[activeTabIndex]) {
        tabs[activeTabIndex].webContents.goBack();
    }
});

globalShortcut.register('CommandOrControl+>', () => {
    if (tabs[activeTabIndex]) {
        tabs[activeTabIndex].webContents.goForward();
    }
});

});

function createNewTab() {
    const tabIndex = tabs.length;
    let view = new BrowserView();
    mainWindow.addBrowserView(view);

    view.setBounds({ x: 0, y: 40, width: 1000, height: 660 });
    view.webContents.loadURL('https://www.google.com');

    tabs.push(view);

    if (activeTabIndex === null) {
        activeTabIndex = 0;
    }

    switchTab(tabIndex);
    mainWindow.webContents.send('add-tab', tabIndex);
}

function switchTab(tabIndex) {
    if (!tabs[tabIndex]) return; // Prevent errors by exiting if the tab doesn't exist

    activeTabIndex = tabIndex;

    tabs.forEach((tab, index) => {
        if (tab) {
            mainWindow.removeBrowserView(tab);
        }
    });

    mainWindow.addBrowserView(tabs[tabIndex]);

    // Adjust bounds to fit the screen, make the window full width and height
    const { width, height } = mainWindow.getBounds(); // Get the window's dimensions
    tabs[tabIndex].setBounds({ x: 0, y: 40, width: width, height: height - 40 }); // Adjust to window size
}

function closeTab(tabIndex) {
    if (tabs.length > 1) {
        mainWindow.removeBrowserView(tabs[tabIndex]); // Properly remove the view
        tabs.splice(tabIndex, 1); // Remove it from the array
        mainWindow.webContents.send('remove-tab', tabIndex);

        if (activeTabIndex === tabIndex) {
            activeTabIndex = Math.max(0, tabIndex - 1);
            switchTab(activeTabIndex);
        }
    } else {
        mainWindow.close(); // Close the app if the last tab is closed
    }
}