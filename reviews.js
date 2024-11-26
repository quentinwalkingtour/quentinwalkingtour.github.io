// URLs des APIs

const guruWalkUrl = "https://www.guruwalk.com/graphapi/v3/walkers/reviews/by_tour?tour_id=57263&page=1&items=20&language=en";
const getYourGuideUrl = "https://travelers-api.getyourguide.com/activities/814552/reviews?limit=20&offset=0&sort=date:desc&language=en";

// Fonction pour récupérer des données depuis une API
async function fetchReviews(url) {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`Erreur API: ${response.statusText}`);
    return response.json();
}

// Fonction pour transformer les données en un format unifié
function transformReviews(guruReviews, getYourGuideReviews) {
    const guruData = guruReviews.reviews.map((review) => ({
        name: review.author.name,
        country: review.author.country,
        rating: review.rating,
        text: review.text,// || "No comment provided.",
        date: review.createdAt,
        source: "GuruWalk",
    }));

    const gygData = getYourGuideReviews.reviews.map((review) => ({
        name: review.author.fullName,
        country: review.author.country,
        rating: review.rating,
        text: review.message,// || "No comment provided.",
        date: new Date(review.created).toLocaleDateString("en-GB"),
        source: "GetYourGuide",
    }));

    return [...guruData, ...gygData]
    .filter(review => review.rating > 4)
    .filter(review => !!review.text)
    .sort(
            (a, b) => new Date(b.date) - new Date(a.date)
        );
}

// Fonction pour afficher les avis dans le DOM
function displayReviews(reviews) {
    const container = document.getElementById("reviews-container");
    container.innerHTML = ""; // Nettoyer le conteneur avant l'ajout

    reviews.forEach((review) => {
        const reviewCard = document.createElement("div");
        reviewCard.className = "review-card";

        reviewCard.innerHTML = `
            <div class="review-header">
                <h3>${review.name} <span>(${review.country})</span></h3>
                <p>${"⭐".repeat(review.rating)}</p>
            </div>
            <p class="review-text">${review.text}</p>
            <p class="review-footer">Source: ${review.source}, Date: ${review.date}</p>
        `;

        container.appendChild(reviewCard);
    });
}

// Fonction principale
async function loadReviews() {
    try {
        const [guruReviews, getYourGuideReviews] = await Promise.all([
            fetchReviews(guruWalkUrl),
            fetchReviews(getYourGuideUrl),
        ]);

        const allReviews = transformReviews(guruReviews, getYourGuideReviews);
        displayReviews(allReviews);
    } catch (error) {
        console.error("Erreur lors du chargement des avis :", error);
    }
}

// Charger les avis au démarrage
document.addEventListener("DOMContentLoaded", loadReviews);
