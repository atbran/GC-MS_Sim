from abc import ABC, abstractmethod

class ParametersInterface(ABC):
    @abstractmethod
    def get_particle_count(self):
        pass

    @abstractmethod
    def get_solvent_rf(self):
        pass

    @abstractmethod
    def get_nonpolar1_rf(self):
        pass

    @abstractmethod
    def get_nonpolar2_rf(self):
        pass

    @abstractmethod
    def get_semipolar1_rf(self):
        pass

    @abstractmethod
    def get_semipolar2_rf(self):
        pass

    @abstractmethod
    def get_polar1_rf(self):
        pass

    @abstractmethod
    def get_polar2_rf(self):
        pass

    @abstractmethod
    def get_verypolar_rf(self):
        pass

    @abstractmethod
    def get_column_length(self):
        pass

    @abstractmethod
    def get_start_temp(self):
        pass

    @abstractmethod
    def get_end_temp(self):
        pass

    @abstractmethod
    def get_ramp_rate(self):
        pass