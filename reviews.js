// Static reviews — data sourced from others/reviews.csv
// Previous API-based version preserved in others/reviews-with-google.js

// ISO 3166-1 alpha-2 codes for flag-icons library (https://github.com/lipis/flag-icons)
const countryIso = {
  "Afghanistan": "af", "Albania": "al", "Algeria": "dz", "Argentina": "ar",
  "Australia": "au", "Austria": "at", "Belgium": "be", "Brazil": "br",
  "Canada": "ca", "Chile": "cl", "China": "cn", "Colombia": "co",
  "Croatia": "hr", "Czech Republic": "cz", "Denmark": "dk", "Egypt": "eg",
  "Finland": "fi", "France": "fr", "Germany": "de", "Greece": "gr",
  "Hong Kong": "hk", "Hungary": "hu", "India": "in", "Indonesia": "id",
  "Ireland": "ie", "Israel": "il", "Italy": "it", "Japan": "jp",
  "Lebanon": "lb", "Malaysia": "my", "Mexico": "mx", "Morocco": "ma",
  "Netherlands": "nl", "New Zealand": "nz", "Norway": "no", "Philippines": "ph",
  "Poland": "pl", "Portugal": "pt", "Romania": "ro", "Russia": "ru",
  "Saudi Arabia": "sa", "Singapore": "sg", "South Africa": "za",
  "South Korea": "kr", "Spain": "es", "Sweden": "se", "Switzerland": "ch",
  "Taiwan": "tw", "Thailand": "th", "Turkey": "tr", "Ukraine": "ua",
  "United Arab Emirates": "ae", "United Kingdom": "gb", "United States": "us",
  "Vietnam": "vn",
};

const platformLogos = {
  "GuruWalk":     "assets/images/icons/guruwalk.png",
  "GetYourGuide": "assets/images/icons/getyourguide.png",
  "Tripadvisor":  "assets/images/icons/tripadvisor.png",
  "Freetours":    "assets/images/icons/freetours.png",
  "Google":       "assets/images/icons/google.png",
};

// Ordered: most compelling/detailed reviews first for maximum impact
const staticReviews = [
  {
    name: "Alison", country: "United Kingdom", rating: 5,
    text: "Really fantastic! I've been fortunate to travel around the world and do many guided walking tours and I have to say Quentin is probably the best I've experienced. His knowledge, passion and sense of humour shine through.",
    source: "GetYourGuide"
  },
  {
    name: "Jason", country: "Canada", rating: 5,
    text: "Quentin is a master of his craft. We were engaged and enthralled from beginning to end! Our finest walking tour experience to date.",
    source: "GuruWalk"
  },
  {
    name: "Sarah", country: "Canada", rating: 5,
    text: "We joined Quentin's tour with our two kids and were worried they might get bored, but they loved it. Quentin kept everyone engaged with stories and humor. One of the highlights of our whole trip!",
    source: "Google"
  },
  {
    name: "Hugh R", country: "Australia", rating: 5,
    text: "Excellent guide, great humour and energy. Quentin treated us as friends, showing us secret passages and quirky corners as well as the key sights.",
    source: "Tripadvisor"
  },
  {
    name: "Kenneth", country: "Singapore", rating: 5,
    text: "Quentin is very engaging and makes you feel at ease and welcome the moment you join the tour. He cracks jokes while sharing information, making the tour enjoyable and lively. You can tell he is passionate and eager to share his knowledge.",
    source: "GuruWalk"
  },
  {
    name: "Noam", country: "Lebanon", rating: 5,
    text: "Quentin did an amazing job from the organization and communication to the tour itself. He is full of passion and knowledge. It was a wonderful time and we learned a lot while enjoying every minute.",
    source: "Freetours"
  },
  {
    name: "Maryann", country: "United States", rating: 5,
    text: "I've been on many GuruWalks over the years, and Quentin rates as one of the best. I highly recommend you choose Quentin's tour!",
    source: "GuruWalk"
  },
  {
    name: "Abbie C", country: "United States", rating: 5,
    text: "Quentin is an amazing tour guide. You can really feel his love for the city and for sharing his hometown. He also gave great restaurant tips and helped avoid tourist traps.",
    source: "Tripadvisor"
  },
  {
    name: "Dogukan Gormus", country: "Turkey", rating: 5,
    text: "Tour with Quentin was just great! He is very friendly and helpful. His storytelling skills make the tour very interesting. Totally recommended!",
    source: "Freetours"
  },
  {
    name: "Manja", country: "Germany", rating: 5,
    text: "Nothing negative to say. Quentin was the perfect guide. Super fun, easy to listen to and clearly passionate.",
    source: "GuruWalk"
  },
  {
    name: "Phil", country: "United Kingdom", rating: 5,
    text: "Very enjoyable tour with the knowledgeable Quentin. Informative, interesting and entertaining.",
    source: "GuruWalk"
  },
  {
    name: "Jennifer", country: "United States", rating: 5,
    text: "Amazing tour! Quentin was extremely knowledgeable and energetic, and happy to answer questions.",
    source: "GetYourGuide"
  },
  {
    name: "Graham M", country: "United States", rating: 5,
    text: "Incredible tour! Quentin was super knowledgeable and made learning everything fun. I had a completely different view of the city after the tour.",
    source: "GetYourGuide"
  },
];

function displayReviews(reviews) {
  const container = document.querySelector(".reviews-section");
  if (!container) return;

  container.innerHTML = "";

  reviews.forEach((review) => {
    const isoCode = countryIso[review.country];
    const flagHtml = isoCode
      ? `<span class="fi fi-${isoCode} review-flag"></span>`
      : `<span class="review-flag review-flag--fallback">🌍</span>`;

    const logo = platformLogos[review.source];

    const card = document.createElement("div");
    card.className = "review-card";
    card.innerHTML = `
      <div class="review-card-header">
        ${flagHtml}
        <div>
          <div class="reviewer">${review.name}</div>
          <div class="reviewer-country">${review.country}</div>
        </div>
      </div>
      <div class="stars">${"⭐".repeat(review.rating)}</div>
      <div class="content">"${review.text}"</div>
      <div class="platform-info">
        ${logo ? `<img src="${logo}" alt="${review.source}" class="platform-logo">` : ""}
        <span>${review.source}</span>
      </div>
    `;
    container.appendChild(card);
  });
}

document.addEventListener("DOMContentLoaded", () => displayReviews(staticReviews));
