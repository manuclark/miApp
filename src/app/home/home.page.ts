import { Component, OnInit, OnDestroy, AfterViewInit, ViewChild, ElementRef } from '@angular/core';
import { IonHeader, IonToolbar, IonTitle, IonContent, IonButton, IonButtons } from '@ionic/angular/standalone';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { AlertController } from '@ionic/angular/standalone';
import { SnakeScoreService, SnakeScore } from '../services/snake-score.service';
import { provideHttpClient } from '@angular/common/http';
import { HttpClientModule } from '@angular/common/http';

interface Position {
  x: number;
  y: number;
}

@Component({
  selector: 'app-home',
  templateUrl: 'home.page.html',
  styleUrls: ['home.page.scss'],
  imports: [IonHeader, IonToolbar, IonTitle, IonContent, IonButton, IonButtons, CommonModule, HttpClientModule, RouterLink],
})
export class HomePage implements OnInit, OnDestroy, AfterViewInit {
  @ViewChild('gameCanvas', { static: false }) canvasRef!: ElementRef<HTMLCanvasElement>;
  
  private ctx!: CanvasRenderingContext2D;
  private snake: Position[] = [];
  private food: Position = { x: 0, y: 0 };
  private direction: string = 'RIGHT';
  private nextDirection: string = 'RIGHT';
  private gameLoop: any;
  private readonly gridSize = 20;
  private readonly tileSize = 20;
  
  score: number = 0;
  gameOver: boolean = false;
  gameStarted: boolean = false;
  topScores: SnakeScore[] = [];

  constructor(
    private alertController: AlertController,
    private scoreService: SnakeScoreService
  ) {}

  ngOnInit() {
    // Agregar listener para teclado
    document.addEventListener('keydown', this.handleKeyPress.bind(this));
    // Cargar los mejores scores
    this.loadTopScores();
  }

  ngOnDestroy() {
    this.stopGame();
    document.removeEventListener('keydown', this.handleKeyPress.bind(this));
  }

  ngAfterViewInit() {
    const canvas = this.canvasRef.nativeElement;
    this.ctx = canvas.getContext('2d')!;
  }

  startGame() {
    this.gameStarted = true;
    this.gameOver = false;
    this.score = 0;
    this.direction = 'RIGHT';
    this.nextDirection = 'RIGHT';
    
    // Inicializar serpiente en el centro
    this.snake = [
      { x: 10, y: 10 },
      { x: 9, y: 10 },
      { x: 8, y: 10 }
    ];
    
    this.spawnFood();
    this.gameLoop = setInterval(() => this.update(), 100);
  }

  stopGame() {
    if (this.gameLoop) {
      clearInterval(this.gameLoop);
      this.gameLoop = null;
    }
  }

  update() {
    this.direction = this.nextDirection;
    
    const head = { ...this.snake[0] };
    
    // Mover la cabeza según la dirección
    switch (this.direction) {
      case 'UP':
        head.y--;
        break;
      case 'DOWN':
        head.y++;
        break;
      case 'LEFT':
        head.x--;
        break;
      case 'RIGHT':
        head.x++;
        break;
    }
    
    // Verificar colisiones con paredes
    if (head.x < 0 || head.x >= this.gridSize || head.y < 0 || head.y >= this.gridSize) {
      this.endGame();
      return;
    }
    
    // Verificar colisión consigo misma
    if (this.snake.some(segment => segment.x === head.x && segment.y === head.y)) {
      this.endGame();
      return;
    }
    
    this.snake.unshift(head);
    
    // Verificar si come la comida
    if (head.x === this.food.x && head.y === this.food.y) {
      this.score += 10;
      this.spawnFood();
    } else {
      this.snake.pop();
    }
    
    this.draw();
  }

  draw() {
    // Limpiar canvas
    this.ctx.fillStyle = '#1e1e1e';
    this.ctx.fillRect(0, 0, this.gridSize * this.tileSize, this.gridSize * this.tileSize);
    
    // Dibujar cuadrícula
    this.ctx.strokeStyle = '#333';
    for (let i = 0; i <= this.gridSize; i++) {
      this.ctx.beginPath();
      this.ctx.moveTo(i * this.tileSize, 0);
      this.ctx.lineTo(i * this.tileSize, this.gridSize * this.tileSize);
      this.ctx.stroke();
      
      this.ctx.beginPath();
      this.ctx.moveTo(0, i * this.tileSize);
      this.ctx.lineTo(this.gridSize * this.tileSize, i * this.tileSize);
      this.ctx.stroke();
    }
    
    // Dibujar serpiente
    this.snake.forEach((segment, index) => {
      this.ctx.fillStyle = index === 0 ? '#4CAF50' : '#8BC34A';
      this.ctx.fillRect(
        segment.x * this.tileSize + 1,
        segment.y * this.tileSize + 1,
        this.tileSize - 2,
        this.tileSize - 2
      );
    });
    
    // Dibujar comida
    this.ctx.fillStyle = '#FF5722';
    this.ctx.beginPath();
    this.ctx.arc(
      this.food.x * this.tileSize + this.tileSize / 2,
      this.food.y * this.tileSize + this.tileSize / 2,
      this.tileSize / 2 - 2,
      0,
      Math.PI * 2
    );
    this.ctx.fill();
  }

  spawnFood() {
    let newFood: Position;
    do {
      newFood = {
        x: Math.floor(Math.random() * this.gridSize),
        y: Math.floor(Math.random() * this.gridSize)
      };
    } while (this.snake.some(segment => segment.x === newFood.x && segment.y === newFood.y));
    
    this.food = newFood;
  }

  handleKeyPress(event: KeyboardEvent) {
    if (!this.gameStarted || this.gameOver) return;
    
    switch (event.key) {
      case 'ArrowUp':
        if (this.direction !== 'DOWN') this.nextDirection = 'UP';
        event.preventDefault();
        break;
      case 'ArrowDown':
        if (this.direction !== 'UP') this.nextDirection = 'DOWN';
        event.preventDefault();
        break;
      case 'ArrowLeft':
        if (this.direction !== 'RIGHT') this.nextDirection = 'LEFT';
        event.preventDefault();
        break;
      case 'ArrowRight':
        if (this.direction !== 'LEFT') this.nextDirection = 'RIGHT';
        event.preventDefault();
        break;
    }
  }

  changeDirection(newDirection: string) {
    if (this.gameOver) return;
    
    switch (newDirection) {
      case 'UP':
        if (this.direction !== 'DOWN') this.nextDirection = 'UP';
        break;
      case 'DOWN':
        if (this.direction !== 'UP') this.nextDirection = 'DOWN';
        break;
      case 'LEFT':
        if (this.direction !== 'RIGHT') this.nextDirection = 'LEFT';
        break;
      case 'RIGHT':
        if (this.direction !== 'LEFT') this.nextDirection = 'RIGHT';
        break;
    }
  }

  async endGame() {
    this.gameOver = true;
    this.stopGame();
    
    // Mostrar alerta para guardar el score
    if (this.score > 0) {
      await this.showSaveScoreAlert();
    }
  }

  async showSaveScoreAlert() {
    const alert = await this.alertController.create({
      header: '¡Game Over!',
      subHeader: `Puntuación: ${this.score}`,
      message: '¿Quieres guardar tu puntuación?',
      inputs: [
        {
          name: 'playerName',
          type: 'text',
          placeholder: 'Escribe tu nombre',
          attributes: {
            maxlength: 100,
            minlength: 2
          }
        }
      ],
      buttons: [
        {
          text: 'Cancelar',
          role: 'cancel',
          cssClass: 'secondary'
        },
        {
          text: 'Guardar',
          handler: (data) => {
            if (data.playerName && data.playerName.trim().length >= 2) {
              this.saveScore(data.playerName.trim());
              return true;
            } else {
              this.showErrorAlert('Por favor, ingresa un nombre válido (mínimo 2 caracteres)');
              return false;
            }
          }
        }
      ]
    });

    await alert.present();
  }

  async showErrorAlert(message: string) {
    const alert = await this.alertController.create({
      header: 'Error',
      message: message,
      buttons: ['OK']
    });
    await alert.present();
  }

  async showSuccessAlert(message: string) {
    const alert = await this.alertController.create({
      header: 'Éxito',
      message: message,
      buttons: ['OK']
    });
    await alert.present();
  }

  saveScore(playerName: string) {
    this.scoreService.saveScore(playerName, this.score).subscribe({
      next: (response) => {
        console.log('Score guardado:', response);
        this.showSuccessAlert(`¡Score guardado exitosamente, ${playerName}!`);
        this.loadTopScores();
      },
      error: (error) => {
        console.error('Error al guardar el score:', error);
        this.showErrorAlert('Error al guardar el score. Por favor, intenta de nuevo.');
      }
    });
  }

  loadTopScores() {
    this.scoreService.getTopScores(10).subscribe({
      next: (scores) => {
        this.topScores = scores;
        console.log('Top scores cargados:', scores);
      },
      error: (error) => {
        console.error('Error al cargar los scores:', error);
      }
    });
  }
}
