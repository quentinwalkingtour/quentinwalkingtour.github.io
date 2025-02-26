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
  
//   async function fetchGoogleReviews(placeId, apiKey) {
//     try {
//       const url = `https://maps.googleapis.com/maps/api/place/details/json?place_id=${placeId}&fields=reviews&key=${apiKey}`;
//       const response = await fetchReviews(url);
      
//       if (!response || !response.result || !response.result.reviews) {
//         throw new Error('Format de réponse Google invalide');
//       }
      
//       return response.result.reviews.map(review => ({
//         name: review.author_name,
//         country: '',
//         rating: review.rating,
//         text: review.text,
//         date: new Date(review.time * 1000).toLocaleDateString("fr-FR"),
//         source: "Google",
//         logo: "assets/images/icons/google.png"
//       }));
//     } catch (error) {
//       console.error("Erreur lors de la récupération des avis Google:", error);
//       return [];
//     }
//   }
  
//   async function fetchTripadvisorReviews(locationId, apiKey) {
//     try {
//       const url = `https://api.content.tripadvisor.com/api/v1/location/${locationId}/reviews`;
//       const response = await fetchReviews(url, {
//         headers: {
//           'Accept': 'application/json',
//           'X-TripAdvisor-API-Key': apiKey
//         }
//       });
//       if (!response || !response.data) {
//         throw new Error('Format de réponse Tripadvisor invalide');
//       }
  
//       return response.data.map(review => ({
//         name: review.user.username,
//         country: '',
//         rating: review.rating,
//         text: review.text,
//         date: new Date(review.published_date).toLocaleDateString("fr-FR"),
//         source: "Tripadvisor",
//         logo: "assets/images/icons/tripadvisor.png"
//       }));
//     } catch (error) {
//       console.error("Erreur lors de la récupération des avis Tripadvisor:", error);
//       return [];
//     }
//   }

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

  function transformReviews(guruReviews, getYourGuideReviews, googleReviews, tripadvisorReviews) {
  const allReviews = [];

  // Process GuruWalk reviews if available
  if (guruReviews && guruReviews.reviews) {
    const guruData = guruReviews.reviews.map((review) => ({
      name: review.author.name,
      country: review.author.country,
      rating: review.rating,
      text: truncateText(review.text),
      date: parseGuruWalkDate(review.createdAt), // Use the specific parser for GuruWalk dates
      source: "GuruWalk",
      logo: "assets/images/icons/guruwalk.png",
    }));
    allReviews.push(...guruData);
  }

  // Process GetYourGuide reviews if available
  if (getYourGuideReviews && getYourGuideReviews.reviews) {
    const gygData = getYourGuideReviews.reviews.map((review) => ({
      name: review.author.fullName,
      country: review.author.country,
      rating: review.rating,
      text: truncateText(review.message),
      date: new Date(review.created), // Store as Date object for better sorting
      source: "GetYourGuide",
      logo: "assets/images/icons/getyourguide.png",
    }));
    allReviews.push(...gygData);
  }

  // Add Google and Tripadvisor reviews
//   allReviews.push(
//     ...googleReviews.map(review => ({
//       ...review,
//       text: truncateText(review.text),
//       date: new Date(review.date) // Convert to Date object for sorting
//     })),
//     ...tripadvisorReviews.map(review => ({
//       ...review,
//       text: truncateText(review.text),
//       date: new Date(review.date) // Convert to Date object for sorting
//     }))
//   );

  return allReviews
    .filter((review) => review.rating > 4)
    .filter((review) => !!review.text)
    .sort((a, b) => b.date - a.date) // Sort by date descending
    .slice(0, 20); // Limit to 10 reviews
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
      <div class="date">${review.date.toLocaleDateString("fr-FR")}</div>
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
      safeApiCall(fetchReviews, guruWalkUrl),
      safeApiCall(fetchReviews, getYourGuideUrl),
    //   safeApiCall(fetchGoogleReviews, googlePlaceId, googleApiKey),
    //   safeApiCall(fetchTripadvisorReviews, tripadvisorLocationId, tripadvisorApiKey)
    ]);
  
    // Extract successful results, using empty arrays/objects for failed calls
    const [guruReviews, getYourGuideReviews, googleReviews, tripadvisorReviews] = results.map(
      result => (result.status === 'fulfilled' && result.value) ? result.value : []
    );
  
    const allReviews = transformReviews(guruReviews, getYourGuideReviews, googleReviews, tripadvisorReviews);
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