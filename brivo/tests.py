from django.test import TestCase
from django.utils import timezone
from datetime import date

from brivo.models import Usuario, Livro, Emprestimo

class EmprestimoTestCase(TestCase):
    def setUp(self):
        # Cria um usuário do tipo aluno
        self.usuario = Usuario.objects.create_user(
            ra='12345',
            nome='João da Silva',
            email='joao@example.com',
            senha='senha123',
            tipo='aluno',
            turma='3A'
        )

        # Cria um livro disponível
        self.livro_disponivel = Livro.objects.create(
            titulo='Livro Disponível',
            autor='Autor 1',
            data_publicacao=date(2020, 1, 1),
            tipo='fisico',
            disponivel=True
        )

        # Cria um livro já indisponível
        self.livro_indisponivel = Livro.objects.create(
            titulo='Livro Indisponível',
            autor='Autor 2',
            data_publicacao=date(2021, 5, 15),
            tipo='fisico',
            disponivel=False
        )

    def test_criacao_usuario(self):
        self.assertEqual(self.usuario.nome, 'João da Silva')
        self.assertTrue(self.usuario.check_password('senha123'))

    def test_criacao_livro(self):
        self.assertTrue(self.livro_disponivel.disponivel)
        self.assertFalse(self.livro_indisponivel.disponivel)

    def test_emprestimo_valido(self):
        emprestimo = Emprestimo.objects.create(
            usuario=self.usuario,
            livro=self.livro_disponivel
        )

        # O livro deve ficar indisponível automaticamente
        self.livro_disponivel.refresh_from_db()
        self.assertFalse(self.livro_disponivel.disponivel)
        self.assertEqual(emprestimo.usuario, self.usuario)
        self.assertEqual(emprestimo.livro, self.livro_disponivel)

    def test_emprestimo_invalido_com_livro_indisponivel(self):
        with self.assertRaisesMessage(ValueError, "Este livro não está disponível para empréstimo."):
            emprestimo = Emprestimo(usuario=self.usuario, livro=self.livro_indisponivel)
            emprestimo.full_clean()  # dispara validações do modelo
            emprestimo.save()

    def test_devolucao(self):
        emprestimo = Emprestimo.objects.create(
            usuario=self.usuario,
            livro=self.livro_disponivel
        )

        # Marcar devolução
        emprestimo.marcar_devolucao()
        emprestimo.refresh_from_db()
        self.assertTrue(emprestimo.devolvido)
        self.assertIsNotNone(emprestimo.data_devolucao)

        # O livro deve voltar a ficar disponível
        emprestimo.livro.refresh_from_db()
        self.assertTrue(emprestimo.livro.disponivel)
