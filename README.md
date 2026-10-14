# Quran Exam App
A Quran learning and examination application built with Django REST Framework. Users can challenge their Quran knowledge through interactive quizzes, earn points for correct answers, and track their progress.

## Features
- **User Authentication:** Register, log in, refresh JWT tokens, and reset forgotten passwords through email.
- **Quran Challenges:** Generate random challenges or choose a specific Surah or Juz.
- **Answer Submission:** Submit answers and receive feedback on correctness.
- **Points System:** Earn points for correct answers.
- **Leaderboard:** View the top users ranked by their total points, with real-time updates through WebSockets.
- **User Profile:** View and update profile information.
- **Password Management:** Change passwords and reset forgotten passwords.
- **Session History:** Review previous challenge attempts.

## Technologies Used
- Python
- Django
- Django REST Framework (DRF)
- JWT Authentication
- Django Channels
- Redis
- Swagger API Documentation

## API Endpoints
### 1. Authentication (`auth`)
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register/` | Register a new user |
| POST | `/api/auth/login/` | Authenticate a user and obtain tokens |
| POST | `/api/auth/refresh/` | Refresh an access token |
| POST | `/api/auth/forget-password/` | Request a password reset email |
| POST | `/api/auth/reset-password/` | Reset a password using a valid token |

### 2. Game (`game`)
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/game/generate/` | Generate a Quran challenge |
| POST | `/api/game/submit/` | Submit an answer to a challenge |

### 3. Quran (`quran`)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/quran/surahs/` | Retrieve Quran Surahs |

### 4. User (`user`)
| Method | Endpoint | Description |
|---|---|---|
| PUT | `/api/user/change-password/` | Change the current user's password |
| GET | `/api/user/history/` | Retrieve the user's challenge history |
| GET | `/api/user/profile/get/` | Retrieve the user's profile |
| PUT | `/api/user/profile/update/` | Update the user's profile |

### 5. Leaderboard (WebSocket)
Connect to the leaderboard WebSocket endpoint:
```text
/ws/leaderboard/
```
Connected clients receive the current leaderboard and subsequent leaderboard updates.

## API Documentation
Explore and test the API using the Swagger documentation endpoint configured in the Django URL settings.

## Author
**Mariam AlMenshawy**
GitHub: [MariamAlMenshawy](https://github.com/MariamAlMenshawy)
