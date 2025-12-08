"""
Dependency injection container for Q&A Practice Application.

Implements simple DI container following SOLID Dependency Inversion principle.
Provides service registration and resolution with proper lifecycle management.
"""

from typing import Dict, Type, TypeVar, Callable, Any

T = TypeVar("T")


class DIContainer:
    """
    Simple dependency injection container.

    Follows SOLID principles by providing loose coupling between
    high-level modules and low-level modules through abstractions.
    """

    def __init__(self) -> None:
        """Initialize empty container."""
        self._services: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable[[], Any]] = {}
        self._singletons: Dict[Type, Any] = {}

    def register_singleton(self, interface: Type[T], implementation: Type[T]) -> None:
        """
        Register a singleton service.

        Args:
            interface: The interface/base class
            implementation: The concrete implementation
        """
        self._services[interface] = implementation

    def register_factory(self, interface: Type[T], factory: Callable[[], T]) -> None:
        """
        Register a factory function for service creation.

        Args:
            interface: The interface type
            factory: Factory function to create instances
        """
        self._factories[interface] = factory

    def resolve(self, interface: Type[T]) -> T:
        """
        Resolve a service instance.

        Args:
            interface: The interface type to resolve

        Returns:
            Service instance

        Raises:
            ValueError: If service is not registered
        """
        # Check if we already have a singleton instance
        if interface in self._singletons:
            return self._singletons[interface]

        # Check for factory registration
        if interface in self._factories:
            instance = self._factories[interface]()
            self._singletons[interface] = instance
            return instance

        # Check for class registration
        if interface in self._services:
            implementation = self._services[interface]
            instance = implementation()
            self._singletons[interface] = instance
            return instance

        raise ValueError(f"Service {interface.__name__} is not registered")

    def register_instance(self, interface: Type[T], instance: T) -> None:
        """
        Register a specific instance as singleton.

        Args:
            interface: The interface type
            instance: The instance to register
        """
        self._singletons[interface] = instance


# Global container instance
container = DIContainer()


def get_container() -> DIContainer:
    """Get the global dependency injection container."""
    return container
