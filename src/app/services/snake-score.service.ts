import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface SnakeScore {
  Id?: number;
  PlayerName: string;
  Score: number;
  GameDate?: string;
  CreatedAt?: string;
}

@Injectable({
  providedIn: 'root'
})
export class SnakeScoreService {
  private apiUrl = 'http://localhost:8000/api/snake-scores';

  constructor(private http: HttpClient) { }

  /**
   * Guardar un nuevo score
   */
  saveScore(playerName: string, score: number): Observable<any> {
    const data: SnakeScore = {
      PlayerName: playerName,
      Score: score
    };
    return this.http.post(`${this.apiUrl}`, data);
  }

  /**
   * Obtener los mejores scores (top 10)
   */
  getTopScores(limit: number = 10): Observable<SnakeScore[]> {
    return this.http.get<SnakeScore[]>(`${this.apiUrl}/top/${limit}`);
  }

  /**
   * Obtener todos los scores de un jugador
   */
  getPlayerScores(playerName: string): Observable<SnakeScore[]> {
    return this.http.get<SnakeScore[]>(`${this.apiUrl}/player/${playerName}`);
  }
}
