import { ChakraProvider, theme, extendTheme } from "@chakra-ui/react";
import Chat from "./pages/Chat";


const mytheme = extendTheme({
  colors: {
    brand: {
      color: "white",
      bg: "#3161ad",
    },

    user: {
      color: "white",
      bg: "#38A169",
    }
  },
  styles: {
    global: {
      body: {
        bg: "#171923",
        // bg: "white",
        color: "white",
      },
    },
  },
});


const App = () => {
  return (
    <ChakraProvider theme={mytheme}>
      <Chat />
    </ChakraProvider>
  );
};

export default App;
