import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { 
  IonHeader, 
  IonToolbar, 
  IonTitle, 
  IonContent, 
  IonCard,
  IonCardHeader,
  IonCardTitle,
  IonCardContent,
  IonList,
  IonItem,
  IonLabel,
  IonBadge,
  IonButton,
  IonButtons,
  IonBackButton,
  IonSearchbar,
  IonRefresher,
  IonRefresherContent,
  IonSpinner
} from '@ionic/angular/standalone';
import { SnakeScoreService, SnakeScore } from '../services/snake-score.service';
import { HttpClientModule } from '@angular/common/http';

@Component({
  selector: 'app-scores',
  templateUrl: './scores.page.html',
  styleUrls: ['./scores.page.scss'],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    HttpClientModule,
    IonHeader,
    IonToolbar,
    IonTitle,
    IonContent,
    IonCard,
    IonCardHeader,
    IonCardTitle,
    IonCardContent,
    IonList,
    IonItem,
    IonLabel,
    IonBadge,
    IonButton,
    IonButtons,
    IonBackButton,
    IonSearchbar,
    IonRefresher,
    IonRefresherContent,
    IonSpinner
  ]
})
export class ScoresPage implements OnInit {
  allScores: SnakeScore[] = [];
  filteredScores: SnakeScore[] = [];
  topScores: SnakeScore[] = [];
  loading: boolean = true;
  searchTerm: string = '';

  constructor(private scoreService: SnakeScoreService) {}

  ngOnInit() {
    this.loadScores();
  }

  loadScores() {
    this.loading = true;
    
    // Cargar los top scores
    this.scoreService.getTopScores(100).subscribe({
      next: (scores) => {
        this.allScores = scores;
        this.filteredScores = scores;
        this.topScores = scores.slice(0, 10);
        this.loading = false;
      },
      error: (error) => {
        console.error('Error al cargar scores:', error);
        this.loading = false;
      }
    });
  }

  handleRefresh(event: any) {
    this.loadScores();
    setTimeout(() => {
      event.target.complete();
    }, 1000);
  }

  filterScores(event: any) {
    const searchTerm = event.target.value?.toLowerCase() || '';
    this.searchTerm = searchTerm;

    if (!searchTerm.trim()) {
      this.filteredScores = this.allScores;
      return;
    }

    this.filteredScores = this.allScores.filter(score => 
      score.PlayerName.toLowerCase().includes(searchTerm)
    );
  }

  getMedalEmoji(index: number): string {
    switch(index) {
      case 0: return '🥇';
      case 1: return '🥈';
      case 2: return '🥉';
      default: return '';
    }
  }

  formatDate(dateString: string | undefined): string {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  getScoreColor(score: number): string {
    if (score >= 300) return 'success';
    if (score >= 200) return 'warning';
    if (score >= 100) return 'primary';
    return 'medium';
  }
}
