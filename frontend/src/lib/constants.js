// Sensor status colors
export const SENSOR_STATUS_COLORS = {
  active: { bg: 'bg-green-100', text: 'text-green-700', dot: 'bg-green-500', label: 'Active' },
  maintenance: { bg: 'bg-yellow-100', text: 'text-yellow-700', dot: 'bg-yellow-500', label: 'Maintenance' },
  error: { bg: 'bg-red-100', text: 'text-red-700', dot: 'bg-red-500', label: 'Error' },
  inactive: { bg: 'bg-gray-100', text: 'text-gray-500', dot: 'bg-gray-400', label: 'Inactive' },
};

// Growth stages
export const GROWTH_STAGES = [
  'Germination',
  'Seedling',
  'Vegetative',
  'Flowering',
  'Fruiting',
  'Maturity',
  'Harvest',
];

// Soil types
export const SOIL_TYPES = [
  'Clay',
  'Sandy',
  'Loamy',
  'Silt',
  'Peat',
  'Chalky',
  'Sandy Loam',
  'Clay Loam',
  'Silty Clay',
  'Red Soil',
  'Black Soil',
  'Alluvial',
];

// Crop types
export const CROP_TYPES = [
  'Rice',
  'Wheat',
  'Corn',
  'Soybean',
  'Cotton',
  'Sugarcane',
  'Tomato',
  'Potato',
  'Onion',
  'Chili',
  'Groundnut',
  'Sunflower',
  'Millet',
  'Barley',
  'Other',
];

// Sensor types
export const SENSOR_TYPES = [
  'soil_moisture',
  'temperature',
  'humidity',
  'ph',
  'nutrient',
  'rain_gauge',
];

// Weather condition emojis
export const WEATHER_EMOJIS = {
  Clear: '☀️',
  Clouds: '☁️',
  Rain: '🌧️',
  Drizzle: '🌦️',
  Thunderstorm: '⛈️',
  Snow: '❄️',
  Mist: '🌫️',
  Haze: '🌫️',
  Fog: '🌫️',
  Smoke: '🌫️',
  Dust: '🌪️',
  default: '🌤️',
};

// Seasons
export const SEASONS = [
  'Kharif (Monsoon)',
  'Rabi (Winter)',
  'Zaid (Summer)',
  'Year-round',
];

// Navigation links
export const NAV_LINKS = [
  { href: '/', label: 'Dashboard', icon: '📊' },
  { href: '/farmers', label: 'Farmers', icon: '👨‍🌾' },
  { href: '/fields', label: 'Fields', icon: '🌾' },
  { href: '/crops', label: 'Crops', icon: '🌱' },
  { href: '/sensors', label: 'Sensors', icon: '📡' },
  { href: '/weather', label: 'Weather', icon: '🌤️' },
];
