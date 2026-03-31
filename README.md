# Chinese Self Learning System

A comprehensive web application built with FastAPI and Jinja2 templates for learning Chinese vocabulary with audio pronunciation support.

## Features

### 🏠 **Landing Page**
- Clean, attractive landing page with signup and login options
- Modern gradient design with responsive layout
- Easy navigation to registration and login pages

### 👤 **User Authentication**
- **Registration**: Secure user registration with email validation
- **Login**: User login with session management
- **First-time User Detection**: Special welcome message for new users vs returning users
- **Session Management**: Automatic session handling with cookies

### 🔍 **Search Functionality**
- **Multi-criteria Search**: Search by Chinese characters, pinyin, or English meanings
- **Level Filtering**: Filter words by difficulty level (1-6)
- **Recent Searches**: Browser-based search history for quick access
- **Smart Search Tips**: Helpful hints for different search methods

### 🎵 **Audio Integration**
- **Built-in Audio Player**: Click any word to hear pronunciation
- **TTS Integration**: Uses provided TTS URLs for authentic pronunciation
- **Keyboard Shortcuts**: Spacebar to play/pause, Escape to stop
- **Visual Feedback**: Play buttons change state during audio playback

### 🎨 **Enhanced User Experience**
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Smooth Animations**: Fade-in effects and hover animations
- **Color-coded Levels**: Different colors for different difficulty levels
- **Keyboard Navigation**: Navigate word cards with arrow keys
- **Accessibility**: Proper ARIA labels and keyboard support

## Technical Implementation

### Backend (FastAPI)
- **Database**: MySQL with users, sessions, and words tables
- **Security**: Password hashing with bcrypt
- **Session Management**: Token-based authentication with cookies
- **Error Handling**: Comprehensive error handling and user feedback

### Frontend (Jinja2 + CSS + JavaScript)
- **Templates**: Clean, modular Jinja2 templates
- **Styling**: Modern CSS with CSS variables for easy theming
- **JavaScript**: Vanilla JS for audio playback and interactivity
- **Responsive**: Mobile-first responsive design

### Database Schema

#### Users Table
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL
);
```

#### Sessions Table
```sql
CREATE TABLE sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    token VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

#### Words Table
```sql
-- Provided by user, contains:
-- level, hanzi, pinyin, pinyin_tone, pinyin_num, english, pos, tts_url
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- MySQL database
- Required Python packages (see below)

### 1. Install Dependencies
```bash
pip install fastapi uvicorn mysql-connector-python bcrypt jinja2
```

### 2. Database Setup
1. Create MySQL database named `cls`
2. Run the application - tables will be created automatically
3. Import your Chinese words data into the `words` table

### 3. Configuration
Update the database configuration in `main.py`:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password',
    'database': 'cls'
}
```

### 4. Populate the Database with Vocabulary
Run the population script to add sample HSK vocabulary:
```bash
python populate_db.py
```

This will add over 150 common Chinese words with audio pronunciation support.

### 5. Run the Application
```bash
python main.py
```

The application will start on `http://127.0.0.1:3000`

## Usage Guide

### For New Users
1. Visit the landing page at `http://127.0.0.1:3000`
2. Click "Sign Up" to create an account
3. Fill in username, email, and password
4. After registration, you'll be automatically logged in and taken to the dashboard

### For Returning Users
1. Visit the landing page
2. Click "Login" and enter your credentials
3. You'll be taken to the dashboard

### Using the Search Feature
1. From the dashboard, click "Search Words"
2. Enter your search term in the search box
3. Optionally select a level to filter by difficulty
4. Click "Search" or press Enter
5. Browse the results and click any word to hear its pronunciation

### Search Methods
- **By Character**: Type Chinese characters (e.g., "少")
- **By Pinyin**: Type pinyin (e.g., "shao")
- **By English**: Type English meanings (e.g., "few")

## Key Features Details

### First-time User Detection
The system tracks whether a user is logging in for the first time by checking if they have any previous sessions. First-time users get a special welcome message.

### Audio Playback
- Each word card has a play button that uses the TTS URL from the database
- Audio playback is handled client-side with JavaScript
- Visual feedback shows when audio is playing
- Keyboard shortcuts for enhanced accessibility

### Search History
- Recent searches are stored in the browser's localStorage
- Quick access buttons appear on the search page
- History persists between sessions

### Responsive Design
- Mobile-friendly layout that adapts to different screen sizes
- Touch-friendly buttons and interactions
- Optimized for both desktop and mobile learning

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check MySQL server is running
   - Verify database credentials in `main.py`
   - Ensure the `cls` database exists

2. **Template Errors**
   - Ensure all template files are in the `templates/` directory
   - Check file permissions

3. **Audio Not Playing**
   - Verify TTS URLs in the database are valid
   - Check browser console for JavaScript errors

### Development Notes

- Templates are cached by default - changes may require server restart
- Static files (CSS, JS) are served from the `static/` directory
- Session tokens expire after 24 hours
- Passwords are securely hashed using bcrypt

## Future Enhancements

Potential improvements that could be added:
- User progress tracking
- Favorite words functionality
- Quiz/gamification features
- Advanced search filters
- Mobile app version
- Admin panel for word management

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or contributions, please use the GitHub repository or contact the development team.