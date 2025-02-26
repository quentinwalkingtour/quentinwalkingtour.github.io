const guruWalkUrlVieuxLyon =
  "https://www.guruwalk.com/graphapi/v3/walkers/reviews/by_tour?tour_id=57263&page=1&items=10&language=en";
const guruWalkUrlCroixRousse =
  "https://www.guruwalk.com/graphapi/v3/walkers/reviews/by_tour?tour_id=59213&page=1&items=10&language=en";

const getYourGuideUrlVieuxLyon =
  "https://travelers-api.getyourguide.com/activities/814552/reviews?limit=10&offset=0&sort=date:desc&language=en";
const getYourGuideUrlCroixRousse =
  "https://travelers-api.getyourguide.com/activities/875834/reviews?limit=10&offset=0&sort=date:desc&language=en";


const googleApiKey = ""
const googlePlaceId = ""

const tripadvisorApiKey = ""
const tripadvisorLocationId = '';


async function fetchReviews(url, options = {}) {
    try {
      const response = await fetch(url, options);
      if (!response.ok) throw new Error(`Erreur API: ${response.statusText}`);
      return response.json();
    } catch (error) {
      console.error(`Erreur lors de la récupération des avis (${url}):`, error);
      return null;
    }
  }


  function parseGuruWalkDate(dateStr) {
    // Split the date string into parts
    const [day, month, year] = dateStr.split('/').map(Number);
    // Create new Date object (months are 0-based in JavaScript)
    return new Date(year, month - 1, day);
  }

  function truncateText(text, maxLength = 180) {
    if (text.length <= maxLength) return text;
    // Find the last space before maxLength to avoid cutting words
    const lastSpace = text.lastIndexOf(' ', maxLength);
    return text.substring(0, lastSpace > 0 ? lastSpace : maxLength) + ' [...]';
  }

  function transformReviews(
    guruReviewsVieuxLyon,
    getYourGuideReviewsVieuxLyon,
    guruReviewsCroixRousse,
    getYourGuideReviewsCroixRousse
  ) {
    const allReviews = [];
  
    // Helper function to process GuruWalk reviews
    function processGuruReviews(reviews, tourName) {
      if (reviews && reviews.reviews) {
        return reviews.reviews.map((review) => ({
          name: review.author.name,
          country: review.author.country,
          rating: review.rating,
          text: truncateText(review.text),
          date: parseGuruWalkDate(review.createdAt), // Use the specific parser for GuruWalk dates
          tour: tourName,
          source: `GuruWalk`, // Indicate the tour
          logo: "assets/images/icons/guruwalk.png",
        }));
      }
      return [];
    }
  
    // Helper function to process GetYourGuide reviews
    function processGYGReviews(reviews, tourName) {
      if (reviews && reviews.reviews) {
        return reviews.reviews.map((review) => ({
          name: review.author.fullName,
          country: review.author.country,
          rating: review.rating,
          text: truncateText(review.message),
          date: new Date(review.created), // Store as Date object for better sorting
          tour: tourName,
          source: `GetYourGuide`, // Indicate the tour
          logo: "assets/images/icons/getyourguide.png",
        }));
      }
      return [];
    }
  
    // Process all reviews
    allReviews.push(
      ...processGuruReviews(guruReviewsVieuxLyon, "Vieux Lyon"),
      ...processGYGReviews(getYourGuideReviewsVieuxLyon, "Vieux Lyon"),
      ...processGuruReviews(guruReviewsCroixRousse, "Croix-Rousse"),
      ...processGYGReviews(getYourGuideReviewsCroixRousse, "Croix-Rousse")
    );
  
    return allReviews
      .filter((review) => review.rating > 4) // Only keep reviews with a rating above 4
      .filter((review) => !!review.text) // Ensure text is not empty
      .sort((a, b) => b.date - a.date) // Sort by date descending
      .slice(0, 20); // Limit to 20 reviews
  }

function displayReviews(reviews) {
  const container = document.querySelector(".reviews-section");
  if (!container) {
    console.error("Container .reviews-section non trouvé");
    return;
  }
  
  container.innerHTML = "";

  if (reviews.length === 0) {
    container.innerHTML = "<p>Aucun avis disponible pour le moment.</p>";
    return;
  }

  reviews.forEach((review) => {
    const reviewCard = document.createElement("div");
    reviewCard.className = "review-card";

    reviewCard.innerHTML = `
      <div class="reviewer">${review.name}${review.country ? ` (${review.country})` : ''}</div>
      <div class="stars">${"⭐".repeat(review.rating)}</div>
      <div class="content">"${review.text}"</div>
      <div class="date">${review.date.toLocaleDateString("fr-FR")} - ${review.tour}</div>
      <div class="platform-info">
        <img src="${review.logo}" alt="${review.source}" class="platform-logo">
        <span>${review.source}</span>
      </div>
    `;

    container.appendChild(reviewCard);
  });
}
  
  async function safeApiCall(apiFunction, ...args) {
    try {
      return await apiFunction(...args);
    } catch (error) {
      console.error(`Erreur lors de l'appel API ${apiFunction.name}:`, error);
      return null;
    }
  }
  
  async function loadReviews() {

    // Use Promise.allSettled to handle each API call independently
    const results = await Promise.allSettled([
      safeApiCall(fetchReviews, guruWalkUrlVieuxLyon),
      safeApiCall(fetchReviews, getYourGuideUrlVieuxLyon),
      safeApiCall(fetchReviews, guruWalkUrlCroixRousse),
      safeApiCall(fetchReviews, getYourGuideUrlCroixRousse),
    ]);
  
    // Extract successful results, using empty arrays/objects for failed calls
    const [guruReviewsVieuxLyon, getYourGuideReviewsVieuxLyon, guruReviewsCroixRousse, getYourGuideReviewsCroixRousse] = results.map(
      result => (result.status === 'fulfilled' && result.value) ? result.value : []
    );
  
    const allReviews = transformReviews(guruReviewsVieuxLyon, getYourGuideReviewsVieuxLyon, guruReviewsCroixRousse, getYourGuideReviewsCroixRousse);
    displayReviews(allReviews);
  
    // Log which sources failed to load
    results.forEach((result, index) => {
      if (result.status === 'rejected') {
        const sources = ['GuruWalk', 'GetYourGuide', 'Google', 'Tripadvisor'];
        console.warn(`Les avis de ${sources[index]} n'ont pas pu être chargés:`, result.reason);
      }
    });
  }
  
  document.addEventListener("DOMContentLoaded", loadReviews);