# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


# ==============================
# Book
# ==============================


class Book(models.Model):
    DISPONIVEL = 'DISPONIVEL'
    EMPRESTADO = 'EMPRESTADO'
    RESERVADO = 'RESERVADO'
    CONSULTA_LOCAL = 'CONSULTA_LOCAL'
    STATUS_CHOICES = (
        (DISPONIVEL, 'Disponível'),
        (EMPRESTADO, 'Emprestado'),
        (RESERVADO, 'Reservado'),
        (CONSULTA_LOCAL, 'Consulta Local'),
    )

    title = models.CharField(
        'Título',
        max_length=150
    )

    ediction = models.CharField(
        'Local de Edição',
        max_length=65
    )

    edictor = models.CharField(
        'Editora',
        max_length=80
    )

    date_ediction = models.DateField(
        'Data de Edição'
    )

    status = models.CharField(
        'Status',
        choices=STATUS_CHOICES,
        max_length=65,
        default=DISPONIVEL
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Livro'
        verbose_name_plural = 'Livros'


# ============================
# Lending
# ============================


class Lending(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='usuario',
        related_name='lendings',
    )

    book = models.ForeignKey(
        Book,
        verbose_name='livro',
        related_name='lendings',
    )

    date_lending = models.DateField(
        'Data do empréstimo',
        auto_now_add=True,
    )

    date_devolution = models.DateField(
        'Data de devolução',
        default=None,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.book.title

    class Meta:
        verbose_name = 'Emprestimo'
        verbose_name_plural = 'Emprestimos'


@receiver(post_save, sender=Lending)
def lending_book_status(sender, instance=None, created=False, **kwargs):
    book = instance.book
    if not instance.date_devolution:
        book.status = Book.EMPRESTADO
    else:
        book.status = Book.DISPONIVEL
    book.save()


@receiver(post_save, sender=Lending)
def remove_previous_reserve(sender, instance=None, created=False, **kwargs):
    if created:
        try:
            reserve = Reserve.objects.get(book=instance.book)
            reserve.delete()
        except ObjectDoesNotExist:
            pass


# =========================
#  Reserve
# =========================


class Reserve(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='usuario',
        related_name='reserves',
    )

    book = models.ForeignKey(
        Book,
        verbose_name='livro',
        related_name='reserves',
    )

    date_reserve = models.DateField(
        'Data da Reserva',
        auto_now_add=True,
    )

    def __str__(self):
        return self.book.title

    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'


@receiver(post_save, sender=Reserve)
def reserve_book_status(sender, instance=None, created=False, **kwargs):
    book = instance.book
    if created:
        book.status = Book.RESERVADO

    book.save()
