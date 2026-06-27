const API = "http://127.0.0.1:3000";

function isVerified(vef){
    const butt = document.getElementById("verifyDiv");
    if (!butt){return false}
    if (vef === undefined || ![true, false].includes(vef)){
        alert("Verification button is undefined");
        butt.innerHTML = `<button id="verifyButton">verify</button>`
        return false;
    }

    if (vef === false){
        butt.innerHTML = `<button id="verifyButton">verify</button>`
        return false;
    }
   
    butt.innerHTML = `<div style="background-color: blue;"id="verifyButton">verified ✅, click to unverify</div>`
    return true;
}

async function me(){
    try{
        const res = await fetch(`${API}/me`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json"
        },
        credentials: "include"
    }
    )
    const data = await res.json();
    const user = data['user'];
    isVerified(user.verified)
    return true

    } catch (err) {
        console.error(err);
        return false
    }
}
async function loadStories() {
  try {
    const res = await fetch(`${API}/user-stories`, {
        method: "GET",
        credentials: "include"
        });
    const data = await res.json();

    const container = document.getElementById("stories");
    container.innerHTML = "";


    const stories = data.stories || [];

    stories.forEach(story => {
      const div = document.createElement("div");
      div.className = "story";

      div.innerHTML = `

      <div>${story.tags || "No content"}</div>
      <br>
        <div>${story.content || "No content"}</div>
        <br>
        <div class="meta">
          by ${story.creator || "unknown"} • ${story.publish_date || ""}
        </div>
        <br>
        <button class="appeal-btn">appeal</button>
      `;

      container.appendChild(div);

      div.querySelector(".appeal-btn").addEventListener("click", () => {
        appeal(story.id);
        });
    });
    

  } catch (err) {
    console.error("Failed to load stories:", err);
  }
}

async function verifyUser(){
    try{

        const res = await fetch(`${API}/verify`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        credentials: "include",
    })
    const data = await res.json();
    isVerified(data.verified);
    } catch (err){
        console.error(err)
    }
}
async function publishStory() {
  const text = document.getElementById("storyText").value;

  if (!text) return alert("Write something first");

  try {
    const res = await fetch(`${API}/publish`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      credentials: "include",
      body: JSON.stringify({ text })
    });

    const data = await res.json();

    if (!res.ok) {
      alert(data.error || "Failed to publish");
      return;
    }

    document.getElementById("storyText").value = "";
    loadStories(); 

  } catch (err) {
    console.error("Publish failed:", err);
  }
}

async function appeal(storyId) {

  try {
    const res = await fetch(`${API}/appeal`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      credentials: "include",
      body: JSON.stringify({story_id: storyId})
    });

    const data = await res.json();

    if (!res.ok) {
      alert(data.error || "Failed to appeal");
      return;
    }


  } catch (err) {
    console.error("Appeal failed:", err);
  }
}
document.addEventListener("DOMContentLoaded",()=>{
    const verifyButton = document.getElementById("verifyButton")
    me();
    loadStories();
    if (verifyButton){
        verifyButton.addEventListener("click", ()=>{
            verifyUser();
        })
    }
})
