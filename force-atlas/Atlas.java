import org.gephi.project.api.*;
import org.gephi.data.attributes.api.*;
import org.gephi.graph.api.*;
import org.gephi.*;
import java.awt.Color;
import java.io.File;
import java.io.IOException;
import org.gephi.data.attributes.api.AttributeColumn;
import org.gephi.data.attributes.api.AttributeController;
import org.gephi.data.attributes.api.AttributeModel;
import org.gephi.filters.api.FilterController;
import org.gephi.filters.api.Query;
import org.gephi.filters.api.Range;
import org.gephi.filters.plugin.graph.DegreeRangeBuilder.DegreeRangeFilter;
import org.gephi.graph.api.DirectedGraph;
import org.gephi.graph.api.GraphController;
import org.gephi.graph.api.GraphModel;
import org.gephi.graph.api.GraphView;
import org.gephi.graph.api.UndirectedGraph;
import org.gephi.io.exporter.api.ExportController;
import org.gephi.io.importer.api.Container;
import org.gephi.io.importer.api.EdgeDefault;
import org.gephi.io.importer.api.ImportController;
import org.gephi.io.processor.plugin.DefaultProcessor;
import org.gephi.layout.plugin.force.StepDisplacement;
import org.gephi.layout.plugin.force.yifanHu.YifanHuLayout;
import org.gephi.preview.api.PreviewController;
import org.gephi.preview.api.PreviewModel;
import org.gephi.preview.api.PreviewProperty;
import org.gephi.preview.types.EdgeColor;
import org.gephi.project.api.ProjectController;
import org.gephi.project.api.Workspace;
import org.gephi.ranking.api.Ranking;
import org.gephi.ranking.api.RankingController;
import org.gephi.ranking.api.Transformer;
import org.gephi.ranking.plugin.transformer.AbstractColorTransformer;
import org.gephi.ranking.plugin.transformer.AbstractSizeTransformer;
import org.gephi.statistics.plugin.GraphDistance;
import org.gephi.layout.plugin.forceAtlas2.*;
import org.openide.util.Lookup;


public class Atlas {
	public static void main(String[] args) {
		if (args.length != 2) {
			System.out.println("arguments: input.gexf output.gexf");
			return;
		}

		String input_name = args[0];
		String output_name = args[1];

		ProjectController pc = Lookup.getDefault().lookup(ProjectController.class);
		pc.newProject();
		Workspace workspace = pc.getCurrentWorkspace();

		AttributeModel attributeModel = Lookup.getDefault().lookup(AttributeController.class).getModel();
		GraphModel graphModel = Lookup.getDefault().lookup(GraphController.class).getModel();
		PreviewModel model = Lookup.getDefault().lookup(PreviewController.class).getModel();
		ImportController importController = Lookup.getDefault().lookup(ImportController.class);
		FilterController filterController = Lookup.getDefault().lookup(FilterController.class);
		RankingController rankingController = Lookup.getDefault().lookup(RankingController.class);


		Container container;
		try {
			System.out.println("Opening input file: " + input_name);
		    File file = new File(input_name);
		    container = importController.importFile(file);
		    container.getLoader().setEdgeDefault(EdgeDefault.UNDIRECTED);
		} catch (Exception ex) {
		    ex.printStackTrace();
		    return;
		}

		importController.process(container, new DefaultProcessor(), workspace);

		DirectedGraph graph = graphModel.getDirectedGraph();
		System.out.println("Nodes: " + graph.getNodeCount());
		System.out.println("Edges: " + graph.getEdgeCount());


		Ranking degreeRanking = rankingController.getModel().getRanking(Ranking.NODE_ELEMENT, Ranking.DEGREE_RANKING);
		AbstractColorTransformer colorTransformer = (AbstractColorTransformer) rankingController.getModel().getTransformer(Ranking.NODE_ELEMENT, Transformer.RENDERABLE_COLOR);
		colorTransformer.setColors(new Color[]{new Color(0xFF3C14), new Color(0xFFBD0F), new Color(0x17FF54), new Color(0x29BBFF)});
		colorTransformer.setColorPositions(new float[]{0.0f, 0.33f,0.66f, 1.0f});
		rankingController.transform(degreeRanking,colorTransformer);

		AbstractSizeTransformer sizeTransformer = (AbstractSizeTransformer) rankingController.getModel().getTransformer(Ranking.NODE_ELEMENT, Transformer.RENDERABLE_SIZE);
		sizeTransformer.setMinSize(1);
		sizeTransformer.setMaxSize(40);
		rankingController.transform(degreeRanking,sizeTransformer);


		ForceAtlas2 atlas = new ForceAtlas2(new ForceAtlas2Builder());
		atlas.setGraphModel(graphModel);
		atlas.initAlgo();
		atlas.resetPropertiesValues();
		atlas.setScalingRatio(5.0);
		atlas.setAdjustSizes(true);
		atlas.setOutboundAttractionDistribution(true);
		atlas.setThreadsCount(1);


		atlas.setJitterTolerance(0.9);
		for (int i = 0; i < 2000 && atlas.canAlgo(); i++) {
			atlas.goAlgo();
		}

		atlas.setJitterTolerance(0.1);
		for (int i = 0; i < 1000 && atlas.canAlgo(); i++) {
			atlas.goAlgo();
		}

		atlas.endAlgo();




		ExportController ec = Lookup.getDefault().lookup(ExportController.class);
		try {
			System.out.println("Opening output file: " + output_name);
		    ec.exportFile(new File(output_name));
		} catch (IOException ex) {
		    ex.printStackTrace();
		    return;
		}

	}
}
