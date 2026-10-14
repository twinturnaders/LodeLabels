console.log(
    "🔥 LodeLabels extension loaded"
);


let lastDetection = {
    username: null,
    time: 0
};


function sendSale(username) {

    console.log(
        "🔥 LodeLabels detected sale:",
        username
    );

    fetch(
        "http://127.0.0.1:8765/sale",
        {
            method: "POST",

            headers: {
                "Content-Type": "text/plain"
            },

            body: username
        }
    )
    .then(async response => {

        const body = await response.text();

        console.log(
            "✅ LodeLabels response:",
            response.status,
            body
        );

    })
    .catch(error => {

        console.error(
            "❌ LodeLabels bridge failed:",
            error
        );

    });
}


function checkText(text) {

    if (!text) {
        return;
    }

    text = text
        .trim()
        .replace(/\s+/g, " ");

    const match = text.match(
        /(?:^|\s)([A-Za-z0-9_.-]+) won the auction!/
    );

    if (!match) {
        return;
    }

    const username = match[1];

    const now = Date.now();


    // Ignore duplicate rendering of the same
    // winner for two seconds.
    if (
        username === lastDetection.username &&
        now - lastDetection.time < 2000
    ) {
        return;
    }


    lastDetection = {
        username: username,
        time: now
    };


    sendSale(username);
}


const observer = new MutationObserver(
    (mutations) => {

        for (const mutation of mutations) {

            /*
             * Sometimes React changes text
             * inside an existing element.
             */
            if (
                mutation.type ===
                "characterData"
            ) {

                checkText(
                    mutation.target.textContent
                );

            }


            /*
             * Other times React adds an
             * entirely new element.
             */
            for (
                const node
                of mutation.addedNodes
            ) {

                if (
                    node.nodeType ===
                    Node.TEXT_NODE
                ) {

                    checkText(
                        node.textContent
                    );

                    continue;
                }


                if (
                    node instanceof Element
                ) {

                    checkText(
                        node.textContent
                    );

                }

            }

        }

    }
);


observer.observe(
    document.body,
    {
        childList: true,
        subtree: true,
        characterData: true
    }
);


console.log(
    "🔥 LodeLabels watcher ACTIVE"
);