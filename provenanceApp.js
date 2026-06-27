const route = "http://127.0.0.1:3000"

function toDashboard(){ window.location.href = '../frontend/dashboard.html'}

async function signup(username){


    const response = await fetch(`${route}/signup`, {
                method: 'POST',
                headers: {
                    "Content-Type": "application/json"
                },
                 credentials: "include",
                body: JSON.stringify({username: username})
    })
    if (!response || !response.ok){
        console.error("Fetch failed");
        return
    }
    const data = await response.json();
    if (data['error']){
        console.error(`Error occured during signup process: ${data['error']}`);
        return
    }
    toDashboard();
}



async function login(username){
            const response = await fetch(`${route}/login`, {
                method: 'POST',
                headers: {
                    "Content-Type": "application/json"
                },
                credentials: "include",
                body: JSON.stringify({username: username})
            })
            if (!response || !response.ok){
                console.error("Fetch failed");
                return
            }
            const data = await response.json();
            if (data['error']){
                console.error(`Error occured during signup process: ${data['error']}`);
                return
            }
            toDashboard();
}

async function publish(text){
            const response = await fetch(`${route}/publish`, {
                method: 'POST',
                headers: {
                    "Content-Type": "application/json"
                },
                credentials: "include",
                body: JSON.stringify({text: text})
            })
            if (!response || !response.ok){
                console.error("Fetch failed");
                return
            }
            const data = await response.json();
            if (data['error']){
                console.error(`Error occured during publish process: ${data['error']}`);
                return
            }
}

async function appeal(storyId, details){
            const response = await fetch(`${route}/appeal`, {
                method: 'POST',
                headers: {
                    "Content-Type": "application/json"
                },
                credentials: "include",
                body: JSON.stringify({story_id: storyId, details: details})
            })
            if (!response || !response.ok){
                console.error("Fetch failed");
                return
            }
            const data = await response.json();
            if (data['error']){
                console.error(`Error occured during signup process: ${data['error']}`);
                return
            }
}




document.addEventListener("DOMContentLoaded", async () =>{
    let username = "";
    const userInput = document.getElementById("usernameInput");
    const signupB = document.getElementById("signupButton");
    const loginB = document.getElementById("loginButton");

    if (signupB && userInput && loginB){
        userInput.addEventListener("input", () => {
            username = userInput.value;
        });
        signupB.addEventListener("click",()=>{
           console.log(username);
            signup(username);
        })

        loginB.addEventListener("click",()=>{
           
            login(username);
        })
    }
})
