from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Usuario, Livro, Emprestimo
from .serializers import UsuarioSerializer, LivroSerializer, EmprestimoSerializer
from .permissions import IsAdminOrReadOnly


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.tipo == 'admin':
            return Usuario.objects.all()
        return Usuario.objects.filter(id=user.id)


class LivroViewSet(viewsets.ModelViewSet):
    queryset = Livro.objects.all()
    serializer_class = LivroSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]


class EmprestimoViewSet(viewsets.ModelViewSet):
    queryset = Emprestimo.objects.all()
    serializer_class = EmprestimoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.tipo == 'admin':
            return Emprestimo.objects.all()
        return Emprestimo.objects.filter(usuario=user)

    def perform_create(self, serializer):
        livro = serializer.validated_data['livro']
        if not livro.disponivel:
            return Response({'livro': 'Este livro não está disponível para empréstimo.'}, status=status.HTTP_400_BAD_REQUEST)
        livro.disponivel = False
        livro.save()
        serializer.save(usuario=self.request.user)

    @action(detail=True, methods=['post'], url_path='marcar-devolucao')
    def marcar_devolucao(self, request, pk=None):
        emprestimo = self.get_object()
        if emprestimo.devolvido:
            return Response({'detail': 'Este empréstimo já foi devolvido.'}, status=400)
        emprestimo.marcar_devolucao()
        return Response({'detail': 'Devolução registrada com sucesso.'})
