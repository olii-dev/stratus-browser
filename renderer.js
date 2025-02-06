document.addEventListener("DOMContentLoaded", () => {
    const tabBar = document.getElementById("tab-bar");
    const newTabBtn = document.getElementById("new-tab-btn");

    let tabs = [];

    function addTab(tabIndex) {
        let tab = document.createElement("div");
        tab.classList.add("tab");
        tab.innerHTML = `Tab ${tabIndex + 1} <button class="close-btn">✖</button>`;
        
        const closeBtn = tab.querySelector(".close-btn");

        // Ensure the click event works to close the tab
        closeBtn.addEventListener("click", () => {
            closeTab(tabIndex);
        });

        tab.onclick = () => switchTab(tabIndex);
        tabBar.appendChild(tab);
        tabs.push(tab);
        switchTab(tabIndex);
    }

    function removeTab(tabIndex) {
        tabs[tabIndex].remove();
        tabs.splice(tabIndex, 1);
        if (tabs.length > 0) switchTab(0);
    }

    function switchTab(tabIndex) {
        tabs.forEach((tab, index) => {
            tab.classList.toggle("active", index === tabIndex);
        });
        window.electron.switchTab(tabIndex);
    }

    function closeTab(tabIndex) {
        window.electron.closeTab(tabIndex); // Tell Electron to close the tab
    }

    newTabBtn.addEventListener("click", () => {
        window.electron.newTab();
    });

    window.electron.addTabListener((event, tabIndex) => {
        addTab(tabIndex);
    });

    window.electron.removeTabListener((event, tabIndex) => {
        removeTab(tabIndex);
    });

    addTab(0);
});