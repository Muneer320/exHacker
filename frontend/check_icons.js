const lr = require('lucide-react');
const icons = [
  'HourglassIcon', 'Hourglass', 'Presentation', 'PartyPopper',
  'Database', 'Code2', 'Package', 'FileText', 'Sparkles',
  'TrendingUp', 'Trophy', 'AlertCircle', 'RefreshCw', 'ChevronDown', 'Copy'
];
icons.forEach(i => console.log(i + ':', typeof lr[i] !== 'undefined'));
