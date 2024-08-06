import plotly.graph_objects as go
from abc import ABC, abstractmethod

class FacilitatorBase(ABC):

    class RelevantData:
        pass

    @abstractmethod
    def get_relevant_data(self) -> RelevantData:
        pass

    @abstractmethod
    def generate_traces(self, relevant_data: RelevantData):
        pass

    @abstractmethod
    def plot(self, traces) -> go.Figure:
        
        fig = go.Figure()
        fig.add_traces(traces)
        return fig
    
